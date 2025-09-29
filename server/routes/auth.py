from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from schemas.auth import GoogleLoginSchema
from schemas.user import UserOut
from db.mongo import db
from utils.jwt_utils import create_jwt
from datetime import datetime, timezone
from core.config import GOOGLE_CLIENT_ID

router = APIRouter()
print("Auth router loaded")


@router.post("/login/google", response_model=dict)
async def google_login(data: GoogleLoginSchema):
    """
    Log in or register a user with Google OAuth.
    Returns a JWT access token and safe user info (UserOut).
    """
    try:
        # Verify Google ID token
        idinfo = id_token.verify_oauth2_token(
            data.id_token, requests.Request(), GOOGLE_CLIENT_ID
        )
        email = idinfo["email"]
        name = idinfo.get("name", "No Name")
        google_id = idinfo["sub"]
        profile_picture = idinfo.get("picture", None)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    now_utc = datetime.now(timezone.utc)

    # Check if user exists
    existing_user = await db.users.find_one({"google_id": google_id})
    if not existing_user:
        result = await db.users.insert_one({
            "google_id": google_id,
            "email": email,
            "name": name,
            "created_at": now_utc,
            "last_login": now_utc,
            "profile_picture": profile_picture,
            "is_active": True
        })
        user_doc = await db.users.find_one({"_id": result.inserted_id})
    else:
        # Update last login
        await db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"last_login": now_utc}}
        )
        user_doc = await db.users.find_one({"_id": existing_user["_id"]})

    # Create JWT (18 hours expiry by default)
    token, _ = create_jwt(str(user_doc["_id"]), email)

    # Return JWT + safe user info
    return {
        "access_token": token,
        "user": UserOut(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc["name"],
            profile_picture=user_doc.get("profile_picture"),
            created_at=user_doc["created_at"],
            last_login=user_doc["last_login"]
        )
    }
