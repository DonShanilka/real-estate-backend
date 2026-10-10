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
        current_user_id: int,   # Logged in user (Admin=3 or Buyer=4)
        other_user_id: int      # Selected user
    ):
        messages = db.query(Message).filter(
            or_(
                and_(
                    Message.sender_id == current_user_id,
                    Message.receiver_id == other_user_id
                ),
                and_(
                    Message.sender_id == other_user_id,
                    Message.receiver_id == current_user_id
                )
            )
        ).order_by(Message.created_at.asc()).all()
    
        return messages

    @staticmethod
    def get_property_conversation(
        db: Session,
        current_user_id: int,
        other_user_id: int,
        property_id: int,
    ):
        return (
            db.query(Message)
            .filter(
                Message.property_id == property_id,
                or_(
                    and_(Message.sender_id == current_user_id, Message.receiver_id == other_user_id),
                    and_(Message.sender_id == other_user_id, Message.receiver_id == current_user_id),
                ),
            )
            .order_by(Message.created_at.asc())
            .all()
        )

    @staticmethod
    def get_agent_conversation(db: Session, agent_id: int, buyer_id: int):
        from app.modules.property.property_model import Property

        return (
            db.query(Message)
            .join(Property, Message.property_id == Property.id)
            .filter(
                Property.agent_id == agent_id,
                or_(
                    and_(Message.sender_id == agent_id, Message.receiver_id == buyer_id),
                    and_(Message.sender_id == buyer_id, Message.receiver_id == agent_id),
                ),
            )
            .order_by(Message.created_at.asc())
            .all()
        )

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

    @staticmethod
    def get_agent_messages(db: Session, agent_id: int):
        from app.modules.property.property_model import Property

        return (
            db.query(Message)
            .join(Property, Message.property_id == Property.id)
            .filter(
                Property.agent_id == agent_id,
                or_(Message.sender_id == agent_id, Message.receiver_id == agent_id),
            )
            .order_by(Message.created_at.desc())
            .all()
        )

    @staticmethod
    def get_agent_inbox(db: Session, agent_id: int):
        from app.modules.property.property_model import Property
        from app.modules.users.user_model import User

        messages = (
            db.query(Message)
            .join(Property, Message.property_id == Property.id)
            .filter(
                Property.agent_id == agent_id,
                or_(Message.sender_id == agent_id, Message.receiver_id == agent_id),
            )
            .order_by(Message.created_at.asc())
            .all()
        )
        threads = {}
        for message in messages:
            buyer_id = message.receiver_id if message.sender_id == agent_id else message.sender_id
            key = (message.property_id, buyer_id)
            thread = threads.setdefault(key, {"messages": [], "unread_count": 0})
            thread["messages"].append(message)
            if message.receiver_id == agent_id and not message.is_read:
                thread["unread_count"] += 1

        output = []
        for (property_id, buyer_id), thread in threads.items():
            property_data = db.query(Property).filter(Property.id == property_id).first()
            buyer = db.query(User).filter(User.id == buyer_id).first()
            if not property_data or not buyer or buyer.role.value != "BUYER":
                continue
            output.append({
                "property_id": property_id,
                "property_title": property_data.title,
                "buyer_id": buyer.id,
                "buyer_name": buyer.full_name,
                "buyer_email": buyer.email,
                "last_message": thread["messages"][-1],
                "unread_count": thread["unread_count"],
            })
        return sorted(output, key=lambda item: item["last_message"].created_at, reverse=True)
