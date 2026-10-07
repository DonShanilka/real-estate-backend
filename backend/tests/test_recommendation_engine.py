import unittest
from types import SimpleNamespace

from app.modules.recommendations.recommendation_engine import RecommendationEngine


def property_listing(property_id, **overrides):
    values = {
        "id": property_id,
        "property_type": "HOUSE",
        "city": "Colombo",
        "district": "Colombo",
        "country": "Sri Lanka",
        "bedrooms": 3,
        "bathrooms": 2,
        "price": 300_000,
        "area_size": 2_000,
        "latitude": 6.9271,
        "longitude": 79.8612,
        "status": "AVAILABLE",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class RecommendationEngineTests(unittest.TestCase):
    def test_exact_match_ranks_ahead_of_different_listing(self):
        target = property_listing(1)
        exact_match = property_listing(2)
        different = property_listing(
            3,
            property_type="LAND",
            city="Kandy",
            district="Kandy",
            bedrooms=0,
            bathrooms=0,
            price=50_000,
            area_size=500,
            latitude=7.2906,
            longitude=80.6337,
        )

        results = RecommendationEngine.recommend(target, [different, exact_match])

        self.assertEqual([item.id for item in results], [2, 3])
        self.assertGreater(
            RecommendationEngine.score(target, exact_match),
            RecommendationEngine.score(target, different),
        )

    def test_excludes_target_applies_limit_and_handles_missing_coordinates(self):
        target = property_listing(1)
        without_location = property_listing(2, latitude=None, longitude=None)
        nearby = property_listing(3, latitude=6.93, longitude=79.86)

        results = RecommendationEngine.recommend(
            target,
            [target, without_location, nearby],
            limit=1,
        )

        self.assertEqual([item.id for item in results], [2])
        self.assertEqual(RecommendationEngine.score(target, without_location), 100.0)
        self.assertEqual(RecommendationEngine.recommend(target, [nearby], limit=0), [])

    def test_only_compares_fields_present_on_both_listings(self):
        target = SimpleNamespace(id=1, city="Colombo")
        candidate = SimpleNamespace(id=2, city="Colombo")

        self.assertEqual(RecommendationEngine.score(target, candidate), 100.0)


if __name__ == "__main__":
    unittest.main()
