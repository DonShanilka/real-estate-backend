from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from .serach_schema import NaturalSearchRequest, NearbySearchQuery, SearchQuery
from .search_controller import SearchController
from .search_service import SearchService

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.post("/natural")
def natural_language_search(
    request: NaturalSearchRequest,
    db: Session = Depends(get_db),
):
    return SearchController.natural_search(request.query, db)


@router.get("/nearby")
def search_nearby_properties(
    filters: NearbySearchQuery = Depends(),
    db: Session = Depends(get_db),
):
    results = SearchService.search_nearby(
        db,
        filters.latitude,
        filters.longitude,
        filters.radius_km,
        filters.limit,
    )
    return {
        "success": True,
        "origin": {"latitude": filters.latitude, "longitude": filters.longitude},
        "radius_km": filters.radius_km,
        "count": len(results),
        "data": results,
    }


@router.get("/")
def search_properties(
    filters: SearchQuery = Depends(),
    db: Session = Depends(get_db)
):
    return SearchController.search(filters, db)