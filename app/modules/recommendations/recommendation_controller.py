from sqlalchemy.orm import Session

from .recommendation_service import RecommendationService


class RecommendationController:

    @staticmethod
    def recommend(
        property_id: int,
        db: Session
    ):
        return RecommendationService.recommend(
            db,
            property_id
        )