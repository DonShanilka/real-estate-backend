from sqlalchemy.orm import Session
from .serach_repository import SearchRepository


class SearchService:

    @staticmethod
    def search_nearby(db: Session, latitude: float, longitude: float, radius_km: float, limit: int):
        return SearchRepository.search_nearby(db, latitude, longitude, radius_km, limit)

    @staticmethod
    def search(db: Session, filters):
        return SearchRepository.search_properties(db, filters)