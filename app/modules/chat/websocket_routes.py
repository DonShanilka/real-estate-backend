from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int
):

    await manager.connect(
        user_id,
        websocket
    )

    try:

        while True:

            data = await websocket.receive_json()

            receiver_id = data["receiver_id"]

            await manager.send_personal_message(
                receiver_id,
                {
                    "from": user_id,
                    "message": data["message"]
                }
            )

    except WebSocketDisconnect:

        print(f"User {user_id} disconnected")