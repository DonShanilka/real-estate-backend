from sqlalchemy.orm import Session
from .review_model import Review


class ReviewRepository:
    
    @staticmethod
    def create_review(db: Session, user_id: int, data):
        
        review = Review(user_id = user_id, property_id = data.property_id, rating = data.rating, comment = data.comment)
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        return {
            "success": True,
            "message": "Review created",
            "data": review
        }
        
    
    @staticmethod
    def get_property_review(db: Session, property_id: int):

        reviews = db.query(Review).filter(Review.property_id == property_id).all()
        
        return reviews
    
    