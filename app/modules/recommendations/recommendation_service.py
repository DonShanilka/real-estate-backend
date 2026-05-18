from sqlalchemy.orm import Session

from .recommendation_repository import RecommendationRepository


class RecommendationService:

    @staticmethod
    def recommend(
        db: Session,
        property_id: int
    ):
        return RecommendationRepository.get_recommendations(
            db,
            property_id
        )