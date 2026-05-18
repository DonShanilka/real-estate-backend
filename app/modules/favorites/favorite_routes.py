from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from .favorite_service import FavoriteService


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


@router.post("/{property_id}")
def add_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return FavoriteService.add(db, user["id"], property_id)


@router.delete("/{property_id}")
def remove_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return FavoriteService.remove(db, user["id"], property_id)


@router.get("/")
def get_favorites(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return FavoriteService.get_all(db, user["id"])