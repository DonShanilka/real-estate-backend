from sqlalchemy.orm import Session

from .recommendation_service import RecommendationService


class RecommendationController:

    @staticmethod
    def recommend(
        property_id: int,
        db: Session,
        limit: int = 10,
    ):
        return RecommendationService.recommend(
            db,
            property_id,
            limit,
        )