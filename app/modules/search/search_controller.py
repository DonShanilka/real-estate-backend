from sqlalchemy.orm import Session
from .search_service import SearchService


class SearchController:

    @staticmethod
    def search(filters, db: Session):
        return SearchService.search(db, filters)

    @staticmethod
    def natural_search(text: str, db: Session):
        return SearchService.natural_search(db, text)