from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from .review_schema import ReviewCreate
from .review_service import ReviewService


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.post("/{property_id}")
def create_review(
    property_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ReviewService.create(
        db,
        user["id"],
        property_id,
        review.rating,
        review.comment
    )


@router.get("/{property_id}")
def get_reviews(
    property_id: int,
    db: Session = Depends(get_db)
):
    return ReviewService.get_reviews(
        db,
        property_id
    )


