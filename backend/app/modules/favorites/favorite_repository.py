from sqlalchemy.orm import Session
from app.modules.favorites.favorite_model import Favorite


class FavoriteRepository:

    @staticmethod
    def add(db: Session, user_id: int, property_id: int):

        existing = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.property_id == property_id
        ).first()

        if existing:
            return {"message": "Already in favorites"}

        fav = Favorite(
            user_id=user_id,
            property_id=property_id
        )

        db.add(fav)
        db.commit()
        db.refresh(fav)

        return fav

    @staticmethod
    def remove(db: Session, user_id: int, property_id: int):

        fav = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.property_id == property_id
        ).first()

        if fav:
            db.delete(fav)
            db.commit()

        return {"message": "Removed"}

    @staticmethod
    def get_all(db: Session, user_id: int):

        return db.query(Favorite).filter(
            Favorite.user_id == user_id
        ).all()