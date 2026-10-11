from sqlalchemy.orm import Session
from sqlalchemy import and_

from .booking_model import Booking
from app.modules.property.property_model import Property
from app.modules.users.user_model import User
from fastapi import HTTPException


class BookingRepository:

    @staticmethod
    def create_booking(
        db: Session,
        user_id: int,
        property_id: int,
        check_in,
        check_out
    ):

        # Check property
        property_data = db.query(Property).filter(
            Property.id == property_id
        ).first()

        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        if not property_data.agent_id:
            raise HTTPException(
                status_code=409,
                detail="This property does not have an assigned agent yet",
            )

        # Prevent double booking
        existing_booking = db.query(Booking).filter(
            Booking.property_id == property_id,
            Booking.status != "cancelled",
            and_(
                Booking.check_in < check_out,
                Booking.check_out > check_in
            )
        ).first()

        if existing_booking:
            raise HTTPException(
                status_code=409,
                detail="Property already booked for selected dates",
            )

        if check_out <= check_in:
            raise HTTPException(status_code=422, detail="Check-out must be after check-in")

        days = (check_out - check_in).days

        total_price = days * property_data.price

        booking = Booking(
            user_id=user_id,
            property_id=property_id,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return booking

    @staticmethod
    def get_all_bookings(db: Session):

        return db.query(Booking).all()

    @staticmethod
    def get_user_bookings(
        db: Session,
        user_id: int
    ):

        return db.query(Booking).filter(
            Booking.user_id == user_id
        ).all()

    @staticmethod
    def get_agent_bookings(db: Session, agent_id: int):
        rows = (
            db.query(Booking, Property, User)
            .join(Property, Booking.property_id == Property.id)
            .join(User, Booking.user_id == User.id)
            .filter(Property.agent_id == agent_id)
            .order_by(Booking.created_at.desc())
            .all()
        )
        return [
            {
                "id": booking.id,
                "user_id": booking.user_id,
                "property_id": property_data.id,
                "check_in": booking.check_in,
                "check_out": booking.check_out,
                "total_price": booking.total_price,
                "status": booking.status,
                "created_at": booking.created_at,
                "buyer": {
                    "id": buyer.id,
                    "full_name": buyer.full_name,
                    "email": buyer.email,
                    "phone": buyer.phone,
                },
                "property": {
                    "id": property_data.id,
                    "title": property_data.title,
                    "address": property_data.address,
                    "city": property_data.city,
                    "image_url": property_data.image_url,
                },
            }
            for booking, property_data, buyer in rows
        ]

    @staticmethod
    def update_booking_status(
        db: Session,
        booking_id: int,
        status: str,
        actor_id: int,
    ):

        status = status.strip().lower()
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        actor = db.query(User).filter(User.id == actor_id).first()
        property_data = db.query(Property).filter(Property.id == booking.property_id).first()
        if not actor or not actor.is_active:
            raise HTTPException(status_code=401, detail="Authenticated user not found")
        if actor.role.value == "ADMIN":
            pass
        elif actor.role.value == "AGENT" and property_data.agent_id == actor_id:
            pass
        elif actor.role.value == "BUYER" and booking.user_id == actor_id and status == "cancelled":
            pass
        else:
            raise HTTPException(status_code=403, detail="You cannot update this booking")

        if status not in {"pending", "confirmed", "cancelled", "completed"}:
            raise HTTPException(status_code=422, detail="Invalid booking status")

        booking.status = status

        db.commit()
        db.refresh(booking)

        return booking

    @staticmethod
    def delete_booking(
        db: Session,
        booking_id: int
    ):

        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "message": "Booking not found"
            }

        db.delete(booking)
        db.commit()

        return {
            "message": "Booking deleted successfully"
        }
