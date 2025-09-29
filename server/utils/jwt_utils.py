import jwt
from datetime import datetime, timedelta
from core.config import JWT_SECRET, JWT_ALGORITHM
from fastapi import Request, HTTPException, Depends


def create_jwt(user_id: str, email: str, hours_valid: int = 18):
    expiration = datetime.utcnow() + timedelta(hours=hours_valid)
    token = jwt.encode(
        {"user_id": user_id, "email": email, "exp": expiration.timestamp()},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    return token, expiration

def decode_jwt(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    try:
        payload = decode_jwt(token)
        return {"user_id": payload["user_id"], "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")