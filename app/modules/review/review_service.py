from sqlalchemy.orm import Session
from .review_repository import ReviewRepository

class ReviewService:
    
    @staticmethod
    def create_review(db: Session, user_id: int, data):
        return ReviewRepository.create_review(db, user_id, data)
    
    
    @staticmethod
    def get_reviews(db: Session, property_id: int):
        return ReviewRepository.get_property_review(db, property_id)
    
    
    @staticmethod
    def update_review(db: Session, review_id: int, data):
        return ReviewRepository.update_review(db, review_id, data)