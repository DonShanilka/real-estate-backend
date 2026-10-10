from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from .chat_schema import MessageCreate
from .chat_service import ChatService
from app.modules.users.user_model import User, UserRole


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/send")
def send_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return ChatService.send(
        db,
        user["id"],
        data.receiver_id,
        data.property_id,
        data.message
    )


@router.get("/conversation/{other_user_id}")
def get_conversation(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)   # ← This returns {"id": 3}
):
    return ChatService.conversation(db, current_user["id"], other_user_id)


@router.get("/property/{property_id}/conversation/{other_user_id}")
def get_property_conversation(
    property_id: int,
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ChatService.property_conversation(
        db, current_user["id"], other_user_id, property_id
    )


@router.get("/my")
def get_my_chats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return ChatService.my_chats(
        db,
        user["id"]
    )


@router.get("/agent/inbox")
def get_agent_inbox(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    actor = db.query(User).filter(User.id == current_user["id"]).first()
    if not actor or not actor.is_active:
        raise HTTPException(status_code=401, detail="Authenticated user not found")
    if actor.role != UserRole.AGENT:
        raise HTTPException(status_code=403, detail="Agent account required")
    return ChatService.agent_inbox(db, actor.id)
