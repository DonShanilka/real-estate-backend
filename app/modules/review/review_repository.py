from sqlalchemy.orm import Session
from sqlalchemy import func

from .review_model import Review


class ReviewRepository:

    @staticmethod
    def create_review(
        db: Session,
        user_id: int,
        property_id: int,
        rating: float,
        comment: str
    ):

        existing_review = db.query(Review).filter(
            Review.user_id == user_id,
            Review.property_id == property_id
        ).first()

        if existing_review:
            return {
                "message": "You already reviewed this property"
            }

        review = Review(
            user_id=user_id,
            property_id=property_id,
            rating=rating,
            comment=comment
        )

        db.add(review)
        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def get_property_reviews(
        db: Session,
        property_id: int
    ):

        return db.query(Review).filter(
            Review.property_id == property_id
        ).all()

    @staticmethod
    def get_average_rating(
        db: Session,
        property_id: int
    ):

        average = db.query(
            func.avg(Review.rating)
        ).filter(
            Review.property_id == property_id
        ).scalar()

        return {
            "property_id": property_id,
            "average_rating": round(average or 0, 1)
        }

    @staticmethod
    def update_review(
        db: Session,
        review_id: int,
        user_id: int,
        rating: float,
        comment: str
    ):

        review = db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()

        if not review:
            return {
                "message": "Review not found"
            }

        review.rating = rating
        review.comment = comment

        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def delete_review(
        db: Session,
        review_id: int,
        user_id: int
    ):

        review = db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()

        if not review:
            return {
                "message": "Review not found"
            }

        db.delete(review)
        db.commit()

        return {
            "message": "Review deleted successfully"
        }