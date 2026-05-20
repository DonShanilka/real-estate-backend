from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from .chat_model import Message


class ChatRepository:

    @staticmethod
    def send_message(
        db: Session,
        sender_id: int,
        receiver_id: int,
        property_id: int,
        message: str
    ):

        new_message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            property_id=property_id,
            message=message
        )

        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        return new_message

    @staticmethod
    def get_conversation(
        db: Session,
        user_id: int,
        other_user_id: int
    ):

        return db.query(Message).filter(
            or_(
                and_(
                    Message.sender_id == user_id,
                    Message.receiver_id == other_user_id
                ),
                and_(
                    Message.sender_id == other_user_id,
                    Message.receiver_id == user_id
                )
            )
        ).order_by(Message.created_at.asc()).all()

    @staticmethod
    def get_my_chats(
        db: Session,
        user_id: int
    ):

        return db.query(Message).filter(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).order_by(Message.created_at.desc()).all()