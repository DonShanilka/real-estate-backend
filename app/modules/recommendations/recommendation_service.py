from sqlalchemy.orm import Session

from .recommendation_repository import RecommendationRepository


class RecommendationService:

    @staticmethod
    def recommend(
        db: Session,
        property_id: int,
        limit: int = 10,
    ):
        return RecommendationRepository.get_recommendations(
            db,
            property_id,
            limit,
        )