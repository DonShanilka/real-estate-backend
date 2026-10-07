import unittest
from types import SimpleNamespace

from app.modules.ai.training.price_prediction_model import (
    MIN_TRAINING_ROWS,
    predict_price,
    train_price_model,
)
from app.modules.ai.price_prediction_service import PricePredictionService
from app.modules.ai.training.price_dataset import load_price_records


def history_rows(count=40):
    cities = ("Colombo", "Kandy", "Galle", "Maharagama")
    rows = []
    for index in range(count):
        bedrooms = 1 + index % 5
        bathrooms = 1 + index % 3
        area = 800 + index * 70
        price = 5_000_000 + bedrooms * 2_000_000 + area * 8_000 + (index % 4) * 500_000
        rows.append(SimpleNamespace(
            city=cities[index % len(cities)],
            district="Colombo" if index % 2 == 0 else "Central",
            country="Sri Lanka",
            property_type="HOUSE" if index % 3 else "APARTMENT",
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            area_size=area,
            land_area_perches=6 + (index % 10),
            price=price,
        ))
    return rows


class PricePredictionModelTests(unittest.TestCase):
    def test_csv_dataset_loads_all_rows_and_status_is_ready(self):
        records = load_price_records()

        self.assertEqual(len(records), 100)
        status = PricePredictionService.training_status()
        self.assertTrue(status["ready"])
        self.assertEqual(status["usable_training_records"], 100)

    def test_predicts_example_property_from_csv_with_cross_validation(self):
        result = PricePredictionService.predict({
            "city": "Colombo", "district": "Colombo", "country": "Sri Lanka",
            "property_type": "HOUSE", "bedrooms": 3, "bathrooms": 2,
            "house_area_sqft": 2200, "land_area_perches": 10,
        })

        self.assertEqual(result["training_rows"], 100)
        self.assertEqual(result["validation"], "5-fold cross-validation")
        self.assertGreater(result["estimated_price_million"], 8)
        self.assertLess(result["estimated_price_million"], 120)
        self.assertEqual(result["unit"], "million")
        self.assertRegex(result["display"]["estimated_market_price"], r"^Rs\. \d+\.\dM$")
        self.assertLessEqual(result["expected_range_million"]["low"], result["estimated_price_million"])
        self.assertGreaterEqual(result["expected_range_million"]["high"], result["estimated_price_million"])
        self.assertNotIn("land_area_perches", result["features_used"])

    def test_requires_sufficient_historical_data(self):
        with self.assertRaisesRegex(ValueError, str(MIN_TRAINING_ROWS)):
            train_price_model(history_rows(MIN_TRAINING_ROWS - 1))

    def test_trains_validates_and_returns_a_price_range(self):
        records = history_rows()
        model = train_price_model(records)
        result = predict_price(model, {
            "city": "Colombo",
            "district": "Colombo",
            "country": "Sri Lanka",
            "property_type": "HOUSE",
            "bedrooms": 3,
            "bathrooms": 2,
            "house_area_sqft": 2200,
            "land_area_perches": 10,
        })

        self.assertGreater(result["estimated_price_million"], 0)
        self.assertLessEqual(result["expected_range_million"]["low"], result["estimated_price_million"])
        self.assertGreaterEqual(result["expected_range_million"]["high"], result["estimated_price_million"])
        self.assertEqual(result["training_rows"], len(records))
        self.assertIn("house_area_sqft", result["features_used"])
        self.assertIn("land_area_perches", result["features_used"])

    def test_discards_invalid_prices_and_imputes_missing_numeric_features(self):
        records = history_rows()
        records.extend([
            SimpleNamespace(price=0, city="Colombo", property_type="HOUSE", bedrooms=3, bathrooms=2, area_size=2000),
            SimpleNamespace(price="not-a-price", city="Colombo", property_type="HOUSE", bedrooms=3, bathrooms=2, area_size=2000),
        ])
        for record in records[:5]:
            record.area_size = None
        for record in records:
            record.land_area_perches = None

        model = train_price_model(records)
        result = predict_price(model, {
            "city": "Colombo",
            "property_type": "HOUSE",
            "bedrooms": 3,
            "bathrooms": 2,
            "house_area_sqft": None,
        })

        self.assertEqual(model.training_rows, 40)
        self.assertGreater(result["estimated_price_million"], 0)
        self.assertNotIn("land_area_perches", result["features_used"])
        self.assertTrue(any("land_area_perches" in note for note in result["limitations"]))


if __name__ == "__main__":
    unittest.main()
