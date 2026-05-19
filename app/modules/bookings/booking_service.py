from sqlalchemy.orm import Session

from .booking_repository import BookingRepository


class BookingService:

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        property_id: int,
        check_in,
        check_out
    ):

        return BookingRepository.create_booking(
            db,
            user_id,
            property_id,
            check_in,
            check_out
        )

    @staticmethod
    def get_all(db: Session):

        return BookingRepository.get_all_bookings(db)

    @staticmethod
    def get_user(
        db: Session,
        user_id: int
    ):

        return BookingRepository.get_user_bookings(
            db,
            user_id
        )

    @staticmethod
    def update_status(
        db: Session,
        booking_id: int,
        status: str
    ):

        return BookingRepository.update_booking_status(
            db,
            booking_id,
            status
        )

    @staticmethod
    def delete(
        db: Session,
        booking_id: int
    ):

        return BookingRepository.delete_booking(
            db,
            booking_id
        )