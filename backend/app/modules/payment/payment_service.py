from sqlalchemy.orm import Session

from app.modules.payment.payment_model import Payment
from app.modules.payment.payment_schema import (
    PaymentCreate,
    PaymentUpdate,
)


def create_payment(
    db: Session,
    payment_data: PaymentCreate,
) -> Payment:
    payment = Payment(**payment_data.model_dump())

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def get_all_payments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Payment]:
    return (
        db.query(Payment)
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_payment_by_id(
    db: Session,
    payment_id: int,
) -> Payment | None:
    return (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )


def get_payments_by_booking(
    db: Session,
    booking_id: int,
) -> list[Payment]:
    return (
        db.query(Payment)
        .filter(Payment.booking_id == booking_id)
        .order_by(Payment.created_at.desc())
        .all()
    )


def get_payments_by_user(
    db: Session,
    user_id: int,
) -> list[Payment]:
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .all()
    )


def update_payment(
    db: Session,
    payment: Payment,
    payment_data: PaymentUpdate,
) -> Payment:
    update_data = payment_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)

    return payment


def delete_payment(
    db: Session,
    payment: Payment,
) -> None:
    db.delete(payment)
    db.commit()