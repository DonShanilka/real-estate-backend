from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

from .serach_schema import SearchQuery
from .search_controller import SearchController
from .search_service import SearchService

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.get("/nearby")
def search_nearby_properties(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10, gt=0, le=500),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = SearchService.search_nearby(db, latitude, longitude, radius_km, limit)
    return {
        "success": True,
        "origin": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "count": len(results),
        "data": results,
    }


@router.get("/")
def search_properties(
    filters: SearchQuery = Depends(),
    db: Session = Depends(get_db)
):
    return SearchController.search(filters, db)