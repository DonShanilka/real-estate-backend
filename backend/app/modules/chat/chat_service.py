from sqlalchemy.orm import Session
from fastapi import HTTPException

from .chat_repository import ChatRepository
from .chat_model import Message
from app.modules.property.property_model import Property
from app.modules.users.user_model import User, UserRole


class ChatService:

    @staticmethod
    def send(
        db: Session,
        sender_id: int,
        receiver_id: int,
        property_id: int,
        message: str
    ):

        if not message or not message.strip():
            raise HTTPException(status_code=422, detail="Message cannot be empty")
        if sender_id == receiver_id:
            raise HTTPException(status_code=422, detail="Cannot message yourself")

        sender = db.query(User).filter(User.id == sender_id).first()
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not sender or not sender.is_active or not receiver or not receiver.is_active:
            raise HTTPException(status_code=404, detail="Active sender and receiver are required")

        if property_id is None and sender.role in {UserRole.BUYER, UserRole.AGENT}:
            raise HTTPException(status_code=422, detail="A property is required for buyer-agent messages")

        if property_id is not None:
            property_data = db.query(Property).filter(Property.id == property_id).first()
            if not property_data:
                raise HTTPException(status_code=404, detail="Property not found")
            if not property_data.agent_id:
                raise HTTPException(status_code=409, detail="This property has no assigned agent")

            if sender.role == UserRole.BUYER:
                if receiver.role != UserRole.AGENT or receiver.id != property_data.agent_id:
                    raise HTTPException(status_code=403, detail="Contact this property's assigned agent")
            elif sender.role == UserRole.AGENT:
                if sender.id != property_data.agent_id or receiver.role != UserRole.BUYER:
                    raise HTTPException(status_code=403, detail="You are not assigned to this property")
                buyer_started_thread = db.query(Message.id).filter(
                    Message.property_id == property_id,
                    Message.sender_id == receiver_id,
                    Message.receiver_id == sender_id,
                ).first()
                if not buyer_started_thread:
                    raise HTTPException(status_code=403, detail="Reply to a buyer's property inquiry first")
            elif sender.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="Buyer or assigned agent account required")

        return ChatRepository.send_message(
            db,
            sender_id,
            receiver_id,
            property_id,
            message
        )

    @staticmethod
    def conversation(db: Session, user_id: int, other_user_id: int):
        actor = db.query(User).filter(User.id == user_id).first()
        if actor and actor.role == UserRole.AGENT:
            other = db.query(User).filter(User.id == other_user_id).first()
            if not other or other.role != UserRole.BUYER:
                raise HTTPException(status_code=403, detail="Agent conversations are limited to buyers")
            return ChatRepository.get_agent_conversation(db, user_id, other_user_id)
        return ChatRepository.get_conversation(db, user_id, other_user_id)

    @staticmethod
    def property_conversation(db: Session, user_id: int, other_user_id: int, property_id: int):
        property_data = db.query(Property).filter(Property.id == property_id).first()
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")

        actor = db.query(User).filter(User.id == user_id).first()
        other = db.query(User).filter(User.id == other_user_id).first()
        if not actor or not other:
            raise HTTPException(status_code=404, detail="Conversation participant not found")

        if actor.role == UserRole.AGENT:
            if actor.id != property_data.agent_id or other.role != UserRole.BUYER:
                raise HTTPException(status_code=403, detail="You are not assigned to this property")
        elif actor.role == UserRole.BUYER:
            if other.id != property_data.agent_id or other.role != UserRole.AGENT:
                raise HTTPException(status_code=403, detail="This is not the property's assigned agent")
        elif actor.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Buyer or assigned agent account required")

        return ChatRepository.get_property_conversation(
            db, user_id, other_user_id, property_id
        )

    @staticmethod
    def my_chats(
        db: Session,
        user_id: int
    ):

        actor = db.query(User).filter(User.id == user_id).first()
        if actor and actor.role == UserRole.AGENT:
            return ChatRepository.get_agent_messages(db, user_id)
        return ChatRepository.get_my_chats(db, user_id)

    @staticmethod
    def agent_inbox(db: Session, agent_id: int):
        return ChatRepository.get_agent_inbox(db, agent_id)

    @staticmethod
    def mark_property_conversation_read(
        db: Session,
        current_user_id: int,
        other_user_id: int,
        property_id: int,
    ):
        # Get the logged-in user.
        actor = (
            db.query(User)
            .filter(User.id == current_user_id)
            .first()
        )

        if not actor or not actor.is_active:
            raise HTTPException(
                status_code=401,
                detail="Active authenticated user required",
            )

        # Get the other participant.
        other = (
            db.query(User)
            .filter(User.id == other_user_id)
            .first()
        )

        if not other or not other.is_active:
            raise HTTPException(
                status_code=404,
                detail="Conversation participant not found",
            )

        # Verify the property exists.
        property_data = (
            db.query(Property)
            .filter(Property.id == property_id)
            .first()
        )

        if not property_data:
            raise HTTPException(
                status_code=404,
                detail="Property not found",
            )

        # Verify the logged-in user can access this conversation.
        if actor.role == UserRole.AGENT:
            if actor.id != property_data.agent_id:
                raise HTTPException(
                    status_code=403,
                    detail="You are not assigned to this property",
                )

            if other.role != UserRole.BUYER:
                raise HTTPException(
                    status_code=403,
                    detail="Agent conversations are limited to buyers",
                )

        elif actor.role == UserRole.BUYER:
            if (
                other.role != UserRole.AGENT
                or other.id != property_data.agent_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="This is not the property's assigned agent",
                )

        elif actor.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to access this conversation",
            )

        # Mark only incoming unread messages as read.
        updated_count = ChatRepository.mark_property_conversation_read(
            db=db,
            current_user_id=current_user_id,
            other_user_id=other_user_id,
            property_id=property_id,
        )

        return {"updated": updated_count}