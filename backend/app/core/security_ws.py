from fastapi import WebSocket, WebSocketException
from jose import jwt, JWTError
from .security import SECRET_KEY, ALGORITHM  # Import from your security file

async def get_current_user_from_ws(websocket: WebSocket):
    """Extract and validate JWT from WebSocket query params"""
    token = websocket.query_params.get("token")
    
    if not token:
        raise WebSocketException(code=1008, reason="Missing token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")

        if user_id is None:
            raise WebSocketException(code=1008, reason="Invalid token")

        return {
            "user_id": int(user_id),
            "role": role
        }

    except JWTError:
        raise WebSocketException(code=1008, reason="Token expired or invalid")