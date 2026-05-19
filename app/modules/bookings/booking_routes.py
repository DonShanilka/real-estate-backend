from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

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

    return BookingService.create(
        db,
        user["id"],
        property_id,
        booking.check_in,
        booking.check_out
    )


@router.get("/")
def get_all_bookings(
    db: Session = Depends(get_db)
):

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


@router.put("/{booking_id}")
def update_booking_status(
    booking_id: int,
    booking: BookingUpdate,
    db: Session = Depends(get_db)
):

    return BookingService.update_status(
        db,
        booking_id,
        booking.status
    )


@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):

    return BookingService.delete(
        db,
        booking_id
    )