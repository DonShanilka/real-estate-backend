from sqlalchemy.orm import Session

from .chat_repository import ChatRepository


class ChatService:

    @staticmethod
    def send(
        db: Session,
        sender_id: int,
        receiver_id: int,
        property_id: int,
        message: str
    ):

        return ChatRepository.send_message(
            db,
            sender_id,
            receiver_id,
            property_id,
            message
        )

    @staticmethod
    def conversation(
        db: Session,
        user_id: int,
        other_user_id: int
    ):

        return ChatRepository.get_conversation(
            db,
            user_id,
            other_user_id
        )

    @staticmethod
    def my_chats(
        db: Session,
        user_id: int
    ):

        return ChatRepository.get_my_chats(
            db,
            user_id
        )