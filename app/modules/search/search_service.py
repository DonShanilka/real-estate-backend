from sqlalchemy.orm import Session
from .natural_language import parse_property_search
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
            return {"success": True, "parsed_filters": {}, "total": 0, "data": []}

        properties = SearchRepository.search_natural_filters(db, filters)
        return {
            "success": True,
            "parsed_filters": parsed_filters,
            "total": len(properties),
            "data": properties,
        }