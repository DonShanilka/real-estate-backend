from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from .chat_schema import MessageCreate
from .chat_service import ChatService


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
    user=Depends(get_current_user)
):

    return ChatService.conversation(
        db,
        user["id"],
        other_user_id
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