from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from .review_schema import (
    ReviewCreate,
    ReviewUpdate
)

from .review_service import ReviewService


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.get("")
def get_all_reviews(
    db: Session = Depends(get_db)
):
    reviews = ReviewService.get_all_reviews(db)
    return [
        {
            "id": review.id,
            "user_id": review.user_id,
            "property_id": review.property_id,
            "rating": review.rating,
            "comment": review.comment,
            "create_at": review.create_at,
            "user": {
                "id": review.user.id,
                "full_name": review.user.full_name,
                "role": getattr(review.user.role, "value", review.user.role),
            } if review.user else None,
            "property": {
                "id": review.property.id,
                "title": review.property.title,
            } if review.property else None,
        }
        for review in reviews
    ]


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


@router.get("/average/{property_id}")
def get_average_rating(
    property_id: int,
    db: Session = Depends(get_db)
):

    return ReviewService.average_rating(
        db,
        property_id
    )


@router.put("/{review_id}")
def update_review(
    review_id: int,
    review: ReviewUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return ReviewService.update(
        db,
        review_id,
        user["id"],
        review.rating,
        review.comment
    )


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return ReviewService.delete(
        db,
        review_id,
        user["id"]
    )