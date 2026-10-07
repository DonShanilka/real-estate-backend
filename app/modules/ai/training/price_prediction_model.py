"""Train and evaluate a conservative Random Forest on recorded property listings."""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

MIN_TRAINING_ROWS = 20
CV_FOLDS = 5
RANGE_COVERAGE = 0.8
CATEGORICAL_FEATURES = ("city", "district", "country", "property_type")
NUMERIC_FEATURES = ("bedrooms", "bathrooms", "house_area_sqft", "land_area_perches")
ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


@dataclass
class TrainedPriceModel:
    model: Pipeline
    mae: float
    r2: float | None
    interval_margin: float
    training_rows: int
    validation_rows: int
    used_features: tuple[str, ...]


def _get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)


def _clean_training_data(records: list[Any]) -> tuple[list[dict[str, Any]], np.ndarray, tuple[str, ...]]:
    rows: list[dict[str, Any]] = []
    prices: list[float] = []

    for record in records:
        try:
            price = float(_get(record, "price"))
        except (TypeError, ValueError):
            continue
        if not np.isfinite(price) or price <= 0:
            continue

        area = _get(record, "area_size")
        try:
            area = float(area) if area is not None else None
        except (TypeError, ValueError):
            area = None
        if area is not None and (not np.isfinite(area) or area <= 0):
            area = None

        property_type = _get(record, "property_type")
        property_type = getattr(property_type, "value", property_type)
        rows.append({
            "city": str(_get(record, "city") or "Unknown").strip().title(),
            "district": str(_get(record, "district") or "Unknown").strip().title(),
            "country": str(_get(record, "country") or "Unknown").strip().title(),
            "property_type": str(property_type or "Unknown").strip().upper(),
            "bedrooms": _get(record, "bedrooms"),
            "bathrooms": _get(record, "bathrooms"),
            # Existing Property.area_size is the only historical area field.
            "house_area_sqft": area,
            # Used automatically once historical rows provide this column.
            "land_area_perches": _get(record, "land_area_perches"),
        })
        prices.append(price)

    if not rows:
        return [], np.asarray([], dtype=float), ()

    # A completely empty field cannot teach a model anything. Exclude it rather
    # than letting sklearn silently drop it or pretending the feature was used.
    used_features = tuple(
        key for key in ALL_FEATURES
        if any(row.get(key) is not None and row.get(key) != "Unknown" for row in rows)
    )
    rows = [{key: row.get(key) for key in used_features} for row in rows]
    return rows, np.asarray(prices, dtype=float), used_features


def _make_pipeline(features: tuple[str, ...], seed: int = 42) -> Pipeline:
    categorical = [name for name in features if name in CATEGORICAL_FEATURES]
    numeric = [name for name in features if name in NUMERIC_FEATURES]
    transformers = []
    if categorical:
        transformers.append((
            "categorical",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("one_hot", OneHotEncoder(handle_unknown="ignore")),
            ]),
            categorical,
        ))
    if numeric:
        transformers.append((
            "numeric",
            Pipeline([("imputer", SimpleImputer(strategy="median"))]),
            numeric,
        ))

    preprocessing = ColumnTransformer(transformers=transformers, remainder="drop")
    return Pipeline([
        ("features", preprocessing),
        ("regressor", RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            max_features=1.0,
            random_state=seed,
            n_jobs=1,
        )),
    ])


def train_price_model(records: list[Any], minimum_rows: int = MIN_TRAINING_ROWS) -> TrainedPriceModel:
    rows, prices, features = _clean_training_data(records)
    if len(rows) < minimum_rows:
        raise ValueError(
            f"Price prediction needs at least {minimum_rows} valid historical property listings; "
            f"only {len(rows)} usable price records are available."
        )
    if len(features) == 0:
        raise ValueError("Training data has no usable property features.")

    frame = pd.DataFrame(rows)
    # Out-of-fold predictions validate every row without scoring it with a model that trained on it.
    predictions = cross_val_predict(
        _make_pipeline(features),
        frame,
        prices,
        cv=KFold(min(CV_FOLDS, len(rows)), shuffle=True, random_state=42),
    )
    residuals = np.abs(prices - predictions)
    mae = float(mean_absolute_error(prices, predictions))
    r2 = float(r2_score(prices, predictions))
    # The range covers RANGE_COVERAGE of cross-validated errors; it is not a guarantee.
    interval_margin = float(np.quantile(residuals, RANGE_COVERAGE))

    final_model = _make_pipeline(features)
    final_model.fit(frame, prices)
    return TrainedPriceModel(
        model=final_model,
        mae=mae,
        r2=r2,
        interval_margin=interval_margin,
        training_rows=len(rows),
        validation_rows=len(rows),
        used_features=features,
    )


def predict_price(model: TrainedPriceModel, request: dict[str, Any]) -> dict[str, Any]:
    property_type = request.get("property_type")
    property_type = getattr(property_type, "value", property_type)
    values = {
        "city": str(request.get("city") or "Unknown").strip().title(),
        "district": str(request.get("district") or "Unknown").strip().title(),
        "country": str(request.get("country") or "Sri Lanka").strip().title(),
        "property_type": str(property_type or "Unknown").strip().upper(),
        "bedrooms": request.get("bedrooms"),
        "bathrooms": request.get("bathrooms"),
        "house_area_sqft": request.get("house_area_sqft"),
        "land_area_perches": request.get("land_area_perches"),
    }
    model_input = {key: values[key] for key in model.used_features}
    estimate = float(model.model.predict(pd.DataFrame([model_input]))[0])
    margin = model.interval_margin
    return {
        "estimated_price": round(estimate, 2),
        "expected_range": {
            "low": round(max(0.0, estimate - margin), 2),
            "high": round(estimate + margin, 2),
        },
        "currency": "LKR",
        "model": "RandomForestRegressor",
        "training_rows": model.training_rows,
        "validation": f"{CV_FOLDS}-fold cross-validation",
        "range_coverage": RANGE_COVERAGE,
        "validation_mae": round(model.mae, 2),
        "validation_r2": round(model.r2, 4) if model.r2 is not None else None,
        "features_used": list(model.used_features),
        "limitations": [
            "Estimate is based on historical listing prices, not verified completed-sale prices.",
            "Expected range is the cross-validated error band covering about 80% of past errors, not a guaranteed valuation.",
            "Historical area_size is assumed to represent house square feet; confirm its unit is consistent.",
            *([] if "land_area_perches" in model.used_features else [
                "Historical land_area_perches is unavailable, so land area was not used by this model."
            ]),
        ],
    }
