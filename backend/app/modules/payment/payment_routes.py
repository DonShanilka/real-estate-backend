from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.bookings.booking_model import Booking
from app.modules.users.user_model import User

from app.modules.payment.payment_model import Payment
from app.modules.payment.payment_schema import (
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
)
from app.modules.payment import payment_service


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)

@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.id == payment_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    booking = db.query(Booking).filter(
        Booking.id == payment_data.booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.user_id != payment_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking does not belong to this user",
        )

    try:
        return payment_service.create_payment(
            db,
            payment_data,
        )
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create payment. Check transaction ID.",
        )


@router.get(
    "/",
    response_model=list[PaymentResponse],
)
def get_all_payments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return payment_service.get_all_payments(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/booking/{booking_id}",
    response_model=list[PaymentResponse],
)
def get_payments_by_booking(
    booking_id: int,
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return payment_service.get_payments_by_booking(
        db,
        booking_id,
    )


@router.get(
    "/user/{user_id}",
    response_model=list[PaymentResponse],
)
def get_payments_by_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return payment_service.get_payments_by_user(
        db,
        user_id,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment_by_id(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = payment_service.get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


@router.put(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
):
    payment = payment_service.get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    try:
        return payment_service.update_payment(
            db,
            payment,
            payment_data,
        )
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update payment. Check transaction ID.",
        )


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = payment_service.get_payment_by_id(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    payment_service.delete_payment(db, payment)

    return None