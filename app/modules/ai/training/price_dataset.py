"""Load the historical property dataset used to train the price model."""

import csv
from pathlib import Path
from types import SimpleNamespace

DATASET_PATH = Path(__file__).resolve().parents[3] / "csv" / "real_estate_100_dataset.csv"


def load_price_records(path: Path = DATASET_PATH) -> list[SimpleNamespace]:
    """Read CSV rows into the record shape expected by train_price_model."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    return [
        SimpleNamespace(
            price=row.get("price"),
            city=row.get("city"),
            district=row.get("district"),
            country=row.get("country"),
            property_type=row.get("property_type"),
            bedrooms=_number(row.get("bedrooms")),
            bathrooms=_number(row.get("bathrooms")),
            area_size=row.get("area"),
        )
        for row in rows
    ]


def _number(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None
