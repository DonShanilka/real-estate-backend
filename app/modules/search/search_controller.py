from fastapi import Depends
from sqlalchemy.orm import Session

# from app.core.database import Base
from .serach_schema import SearchQuery
from .search_service import SearchService

class SearchController:
    
    @staticmethod
    def search(filters: SearchQuery, db: Session):
        return SearchService.search(db, filters)