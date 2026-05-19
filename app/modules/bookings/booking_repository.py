from sqlalchemy.orm import Session
from sqlalchemy import and_

from .booking_model import Booking
from app.modules.property.property_model import Property


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
            return {
                "message": "Property not found"
            }

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
            return {
                "message": "Property already booked for selected dates"
            }

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
    def update_booking_status(
        db: Session,
        booking_id: int,
        status: str
    ):

        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "message": "Booking not found"
            }

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