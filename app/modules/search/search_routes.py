from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import Base

from .serach_schema import SearchQuery
from .search_controller import SearchController

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@router.get("/")
def search_properties(
    filters: SearchQuery = Depends(),
    db: Session = Depends(Base)
):
    return SearchController.search(filters, db)