from sqlalchemy.orm import Session
from .natural_language import parse_property_search
from .natural_search_matching import rank_database_properties
from .serach_repository import SearchRepository


class SearchService:

    @staticmethod
    def search(db: Session, filters):
        return SearchRepository.search_properties(db, filters)

    @staticmethod
    def natural_search(db: Session, text: str):
        filters = parse_property_search(text)
        parsed_filters = {
            key: value
            for key, value in filters.items()
            if value is not None and (key != "features" or value)
        }
        recognized = any(
            value is not None and value != []
            for value in filters.values()
        )
        if not recognized:
            return {
                "success": True,
                "message": "I couldn't identify property filters in that request. Try specifying a city, property type, bedrooms, budget, or feature.",
                "parsed_filters": {},
                "total": 0,
                "data": [],
            }

        candidates = SearchRepository.get_natural_search_candidates(db)
        ranking = rank_database_properties(candidates, filters)
        properties = ranking["properties"]
        if not properties:
            return {
                "success": True,
                "message": "No property records were found in the database yet. Add listings, then search again.",
                "parsed_filters": parsed_filters,
                "total": 0,
                "data": [],
                "matched_filters": [],
                "relaxed_filters": ranking["relaxed_filters"],
                "unverified_features": ranking["unverified_features"],
            }

        relaxed = ranking["relaxed_filters"]
        if relaxed:
            message = (
                "Showing the closest real listings from your database. "
                "Some requested filters had no exact match: "
                + ", ".join(relaxed)
                + "."
            )
        else:
            message = f"Found {len(properties)} matching propert{'y' if len(properties) == 1 else 'ies'}."
        if ranking["unverified_features"]:
            message += (
                " The database listings do not describe these features, so they "
                "could not be confirmed: "
                + ", ".join(ranking["unverified_features"])
                + "."
            )

        return {
            "success": True,
            "message": message,
            "parsed_filters": parsed_filters,
            "total": len(properties),
            "data": properties,
            "matched_filters": ranking["matched_filters"],
            "relaxed_filters": relaxed,
            "unverified_features": ranking["unverified_features"],
        }