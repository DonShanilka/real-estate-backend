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
    
    
    @staticmethod
    def update_review(db: Session, review_id: int, data):
        
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return {
                "success": False,
                "message": "Review not found"
            }
            
        if data.rating is not None:
            review.rating = data.rating
            
        if data.comment is not None:
            review.comment = data.comment
            
        db.commit()
        db.refresh(review)
        
        return {
            "success": True,
            "message": "Review updated",
            "data": review
        }
        
        
    @staticmethod
    def delete_review(db: Session, review_id: int):
        
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return {
                "success": False,
                "message": "Review not foud"
            }
            
        db.delete(review)
        db.commit()
        
        return {
            "success": True,
            "message": "Review deleted"
        }
        