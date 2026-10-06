from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from .serach_schema import NaturalSearchRequest, SearchQuery
from .search_controller import SearchController

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


@router.get("/")
def search_properties(
    filters: SearchQuery = Depends(),
    db: Session = Depends(get_db)
):
    return SearchController.search(filters, db)