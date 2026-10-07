from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security_ws import get_current_user_from_ws
from .websocket_manager import manager
from .chat_service import ChatService  # If you want to save message

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_ws)   # ← Your JWT validation
):
    user_id = current_user["user_id"]
    role = current_user.get("role", "BUYER")

    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()

            receiver_id = data.get("receiver_id")
            message_text = data.get("message")
            property_id = data.get("property_id")

            if not receiver_id or not message_text:
                continue

            # Save message to database
            new_message = ChatService.send(
                db=db,
                sender_id=user_id,
                receiver_id=receiver_id,
                property_id=property_id,
                message=message_text
            )

            # Broadcast to receiver
            await manager.send_personal_message(
                receiver_id,
                {
                    "id": new_message.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "property_id": property_id,
                    "message": message_text,
                    "is_read": False,
                    "created_at": new_message.created_at.isoformat()
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User {user_id} ({role}) disconnected")