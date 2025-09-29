import jwt
from datetime import datetime, timedelta, timezone
from core.config import JWT_SECRET, JWT_ALGORITHM
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security scheme for Swagger UI
bearer_scheme = HTTPBearer()

def create_jwt(user_id: str, email: str, hours_valid: int = 18):
    """
    Create a JWT token valid for `hours_valid` hours.
    """
    expiration = datetime.now(timezone.utc) + timedelta(hours=hours_valid)
    token = jwt.encode(
        {
            "user_id": user_id,
            "email": email,
            "exp": int(expiration.timestamp())
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    return token, expiration

def decode_jwt(token: str):
    """
    Decode a JWT token and return the payload.
    Raises exception if invalid/expired.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Dependency to get current user from JWT token.
    Works with Swagger UI Authorization lock.
    """
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        return {"user_id": payload["user_id"], "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
