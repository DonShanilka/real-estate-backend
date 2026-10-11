from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.users.user_model import User, UserRole

from .booking_schema import (
    BookingCreate,
    BookingUpdate
)

from .booking_service import BookingService


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


@router.post("/{property_id}")
def create_booking(
    property_id: int,
    booking: BookingCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    actor = db.query(User).filter(User.id == user["id"]).first()
    if not actor or not actor.is_active:
        raise HTTPException(status_code=401, detail="Authenticated user not found")
    if actor.role != UserRole.BUYER:
        raise HTTPException(status_code=403, detail="Buyer account required to request a viewing")

    return BookingService.create(
        db,
        user["id"],
        property_id,
        booking.check_in,
        booking.check_out
    )


@router.get("/")
def get_all_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    actor = db.query(User).filter(User.id == current_user["id"]).first()
    if not actor or not actor.is_active:
        raise HTTPException(status_code=401, detail="Authenticated user not found")
    if actor.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin account required")

    return BookingService.get_all(db)


@router.get("/my")
def get_my_bookings(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return BookingService.get_user(
        db,
        user["id"]
    )


@router.get("/agent")
def get_agent_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    actor = db.query(User).filter(User.id == current_user["id"]).first()
    if not actor or not actor.is_active:
        raise HTTPException(status_code=401, detail="Authenticated user not found")
    if actor.role != UserRole.AGENT:
        raise HTTPException(status_code=403, detail="Agent account required")
    return BookingService.get_agent(db, actor.id)


@router.put("/{booking_id}")
def update_booking_status(
    booking_id: int,
    booking: BookingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return BookingService.update_status(
        db,
        booking_id,
        booking.status,
        current_user["id"],
    )


@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.modules.bookings.booking_model import Booking

    actor = db.query(User).filter(User.id == current_user["id"]).first()
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not actor or not actor.is_active:
        raise HTTPException(status_code=401, detail="Authenticated user not found")
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if actor.role != UserRole.ADMIN and booking.user_id != actor.id:
        raise HTTPException(status_code=403, detail="You cannot delete this booking")
    return BookingService.delete(db, booking_id)
