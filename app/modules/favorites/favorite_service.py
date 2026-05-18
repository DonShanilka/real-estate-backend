from sqlalchemy.orm import Session
from .favorite_repository import FavoriteRepository


class FavoriteService:

    @staticmethod
    def add(db: Session, user_id: int, property_id: int):
        return FavoriteRepository.add_favorite(db, user_id, property_id)

    @staticmethod
    def remove(db: Session, user_id: int, property_id: int):
        return FavoriteRepository.remove_favorite(db, user_id, property_id)

    @staticmethod
    def get_all(db: Session, user_id: int):
        return FavoriteRepository.get_user_favorites(db, user_id)