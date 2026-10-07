from functools import lru_cache

from app.modules.ai.training.price_dataset import DATASET_PATH, load_price_records
from app.modules.ai.training.price_prediction_model import (
    MIN_TRAINING_ROWS,
    predict_price,
    train_price_model,
)


@lru_cache(maxsize=1)
def _trained_model(dataset_mtime: float):
    """Train once per dataset version instead of on every request."""
    return train_price_model(load_price_records())


def _model():
    return _trained_model(DATASET_PATH.stat().st_mtime)


class PricePredictionService:
    @staticmethod
    def training_status() -> dict:
        rows = len(load_price_records())
        return {
            "ready": rows >= MIN_TRAINING_ROWS,
            "dataset": DATASET_PATH.name,
            "usable_training_records": rows,
            "minimum_training_records": MIN_TRAINING_ROWS,
            "model": "RandomForestRegressor",
        }

    @staticmethod
    def predict(property_data: dict) -> dict:
        prediction = predict_price(_model(), property_data)
        prediction["dataset"] = DATASET_PATH.name
        prediction["request"] = {
            key: property_data.get(key)
            for key in (
                "city", "district", "country", "property_type", "bedrooms",
                "bathrooms", "house_area_sqft", "land_area_perches",
            )
        }
        return prediction
