import unittest

from app.modules.search.natural_language import parse_property_search


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


if __name__ == "__main__":
    unittest.main()
