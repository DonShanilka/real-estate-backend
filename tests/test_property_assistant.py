import unittest
from types import SimpleNamespace

from app.modules.ai.inference.property_assistant import answer_property_question


def listing(property_id, **overrides):
    data = {
        "id": property_id,
        "title": f"Family home {property_id}",
        "description": "Modern family house",
        "address": "12 Palm Street",
        "price": 25_000_000,
        "city": "Maharagama",
        "district": "Colombo",
        "property_type": "HOUSE",
        "bedrooms": 3,
        "bathrooms": 2,
        "image_url": None,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


class PropertyAssistantTests(unittest.TestCase):
    def test_family_of_four_recommends_grounded_three_bedroom_listing(self):
        three_bedrooms = listing(124, bedrooms=3)
        one_bedroom = listing(125, bedrooms=1)

        answer = answer_property_question(
            "Which property is best for a family of four?",
            [one_bedroom, three_bedrooms],
        )

        self.assertEqual(answer["recommendation"]["id"], 124)
        self.assertEqual(answer["recommendation"]["bedrooms"], 3)
        self.assertEqual(answer["recommendation"]["bathrooms"], 2)
        self.assertNotIn("parking", answer["recommendation"]["reasons"])
        self.assertEqual(answer["sources"], [124])
        self.assertIn("family would prefer at least 3 bedrooms", answer["answer"])

    def test_matches_requested_location_against_district_column(self):
        answer = answer_property_question(
            "Find a family house in Colombo",
            [listing(1)],
        )

        self.assertEqual(answer["recommendation"]["id"], 1)
        self.assertIn("it is in/near Colombo", answer["recommendation"]["reasons"])

    def test_no_available_listings_does_not_invent_a_recommendation(self):
        answer = answer_property_question("Best house for a family?", [])

        self.assertIsNone(answer["recommendation"])
        self.assertEqual(answer["sources"], [])
        self.assertIn("couldn't find any available properties", answer["answer"])


if __name__ == "__main__":
    unittest.main()
