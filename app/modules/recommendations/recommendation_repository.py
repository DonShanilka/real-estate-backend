from sqlalchemy.orm import Session

from app.modules.property.property_model import Property, PropertyStatus
from .recommendation_engine import RecommendationEngine


class RecommendationRepository:

    @staticmethod
    def get_recommendations(
        db: Session,
        property_id: int,
        limit: int = 10,
    ):
        if limit <= 0:
            return []

        target = db.query(Property).filter(Property.id == property_id).first()
        if target is None:
            return []

        candidates = (
            db.query(Property)
            .filter(
                Property.id != property_id,
                Property.status == PropertyStatus.AVAILABLE,
            )
            .all()
        )
        return RecommendationEngine.recommend(target, candidates, limit)