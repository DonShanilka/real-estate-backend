from sqlalchemy.orm import Session

from .review_repository import ReviewRepository


class ReviewService:

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        property_id: int,
        rating: int,
        comment: str
    ):
        return ReviewRepository.create_review(
            db,
            user_id,
            property_id,
            rating,
            comment
        )

    @staticmethod
    def get_reviews(
        db: Session,
        property_id: int
    ):
        return ReviewRepository.get_property_reviews(
            db,
            property_id
        )

    @staticmethod
    def average_rating(
        db: Session,
        property_id: int
    ):
        return ReviewRepository.get_average_rating(
            db,
            property_id
        )

    
    @staticmethod
    def update(
        db: Session,
        review_id: int,
        user_id: int,
        rating: int,
        comment: str
    ):
        return ReviewRepository.update_review(
            db,
            review_id,
            user_id,
            rating,
            comment
        )

    
    @staticmethod
    def delete(
        db: Session,
        review_id: int,
        user_id: int
    ):
        return ReviewRepository.delete_review(
            db,
            review_id,
            user_id
        )