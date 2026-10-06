import unittest
from unittest.mock import patch
from types import SimpleNamespace

from app.modules.search.natural_language import parse_property_search
from app.modules.search.natural_search_matching import rank_database_properties
from app.modules.search.search_service import SearchService


class NaturalLanguageSearchTests(unittest.TestCase):
    def test_requested_example(self):
        filters = parse_property_search(
            "I need a 3 bedroom house in Colombo under 30 million with parking."
        )

        self.assertEqual(filters["city"], "Colombo")
        self.assertEqual(filters["property_type"], "HOUSE")
        self.assertEqual(filters["bedrooms"], 3)
        self.assertEqual(filters["max_price"], 30_000_000)
        self.assertEqual(filters["features"], ["parking"])

    def test_currency_magnitudes_and_minimum_price(self):
        filters = parse_property_search(
            "2 bedroom apartment in Kandy above LKR 2.5 million"
        )

        self.assertEqual(filters["city"], "Kandy")
        self.assertEqual(filters["property_type"], "APARTMENT")
        self.assertEqual(filters["bedrooms"], 2)
        self.assertEqual(filters["min_price"], 2_500_000)

    def test_unknown_city_name_is_still_parsed_for_database_lookup(self):
        filters = parse_property_search("Find a house in Chilaw with a garden")

        self.assertEqual(filters["city"], "Chilaw")
        self.assertEqual(filters["features"], ["garden"])

    def test_feature_synonyms_and_room_counts(self):
        filters = parse_property_search(
            "Find a 4 bedroom, 3 bathroom villa with a garage and pool under Rs 40,000,000"
        )

        self.assertEqual(filters["bedrooms"], 4)
        self.assertEqual(filters["bathrooms"], 3)
        self.assertEqual(filters["features"], ["parking", "swimming pool"])
        self.assertEqual(filters["max_price"], 40_000_000)

    def test_does_not_invent_unrecognized_filters(self):
        filters = parse_property_search("Looking for a quiet place somewhere")

        self.assertEqual(filters["features"], [])
        self.assertIsNone(filters["city"])
        self.assertIsNone(filters["max_price"])

    @patch("app.modules.search.search_service.SearchRepository.get_natural_search_candidates")
    def test_no_database_matches_returns_helpful_message(self, search):
        search.return_value = []

        response = SearchService.natural_search(
            object(),
            "I need a 2 bedroom house in Kandy under 30 million with parking.",
        )

        self.assertEqual(response["total"], 0)
        self.assertEqual(response["data"], [])
        self.assertIn("No property records were found", response["message"])
        self.assertEqual(response["parsed_filters"]["city"], "Kandy")

    def test_city_can_match_district_and_search_relaxes_unavailable_filters(self):
        listing = SimpleNamespace(
            id=12,
            title="Luxury Villa",
            description="Beautiful modern villa",
            address="12 Palm Street",
            city="Maharagama",
            district="Colombo",
            property_type="HOUSE",
            bedrooms=4,
            bathrooms=2,
            price=250_000,
        )
        filters = parse_property_search(
            "I need a 2 bedroom house in Colombo under 30 million with parking."
        )

        result = rank_database_properties([listing], filters)

        self.assertEqual(result["properties"], [listing])
        self.assertIn("location", result["matched_filters"])
        self.assertIn("bedrooms", result["matched_filters"])
        self.assertIn("features", result["relaxed_filters"])
        self.assertEqual(result["unverified_features"], ["parking"])

    def test_explicit_property_type_excludes_other_database_types(self):
        house = SimpleNamespace(
            id=1, city="Maharagama", district="Colombo", address="Palm Street",
            property_type="HOUSE", bedrooms=4, bathrooms=2, price=250_000,
            title="Family home", description="Modern house",
        )
        villa = SimpleNamespace(
            id=2, city="A", district="A1", address="AAAAA",
            property_type="VILLA", bedrooms=4, bathrooms=46, price=200,
            title="Villa", description="",
        )
        filters = parse_property_search("2 bedroom house in Colombo under 30 million")

        result = rank_database_properties([house, villa], filters)

        self.assertEqual(result["properties"], [house])

    @patch("app.modules.search.search_service.SearchRepository.get_natural_search_candidates")
    def test_matches_return_property_objects_from_database(self, search):
        database_property = SimpleNamespace(
            id=1,
            title="House",
            description="",
            address="",
            city="Colombo",
            district="Colombo",
            property_type="HOUSE",
            bedrooms=3,
            bathrooms=2,
            price=20_000_000,
        )
        search.return_value = [database_property]

        response = SearchService.natural_search(
            object(),
            "3 bedroom house in Colombo under 30 million with parking",
        )

        self.assertEqual(response["total"], 1)
        self.assertIs(response["data"][0], database_property)
        self.assertIn("closest real listings", response["message"])
        self.assertIn("parking", response["message"])


if __name__ == "__main__":
    unittest.main()
