from sqlalchemy.orm import Session
from app.modules.favorites.favorite_model import Favorite


class FavoriteRepository:

    @staticmethod
    def add_favorite(db: Session, user_id: int, property_id: int):

        # check duplicate
        existing = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.property_id == property_id
        ).first()

        if existing:
            return existing

        favorite = Favorite(
            user_id=user_id,
            property_id=property_id
        )

        db.add(favorite)
        db.commit()
        db.refresh(favorite)

        return favorite

    @staticmethod
    def remove_favorite(db: Session, user_id: int, property_id: int):

        favorite = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.property_id == property_id
        ).first()

        if favorite:
            db.delete(favorite)
            db.commit()

        return {"message": "Removed"}

    @staticmethod
    def get_user_favorites(db: Session, user_id: int):

        return db.query(Favorite).filter(
            Favorite.user_id == user_id
        ).all()