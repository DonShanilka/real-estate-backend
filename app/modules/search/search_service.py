from sqlalchemy.orm import Session
from .serach_repository import SearchRepository


class SearchService:

    @staticmethod
    def search(db: Session, filters):
        return SearchRepository.search_properties(db, filters)