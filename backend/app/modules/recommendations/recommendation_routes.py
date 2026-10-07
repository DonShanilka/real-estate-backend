from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

from .recommendation_controller import RecommendationController


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/{property_id}")
def get_recommendations(
    property_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return RecommendationController.recommend(
        property_id,
        db,
        limit,
    )