from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from schemas.auth import GoogleLoginSchema
from db.mongo import db
from utils.jwt_utils import create_jwt
from datetime import datetime

router = APIRouter()
print("Auth router loaded")

@router.post("/login/google")
async def google_login(data: GoogleLoginSchema):
    try:
        idinfo = id_token.verify_oauth2_token(
            data.id_token, requests.Request(), GOOGLE_CLIENT_ID
        )
        email = idinfo["email"]
        name = idinfo.get("name", "No Name")
        google_id = idinfo["sub"]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    # Check MongoDB
    existing_user = await db.users.find_one({"google_id": google_id})
    if not existing_user:
        result = await db.users.insert_one({
            "google_id": google_id,
            "email": email,
            "name": name,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "profile_picture": idinfo.get("picture", None),
            "is_active": True
        })
        user_id = str(result.inserted_id)
    else:
        user_id = str(existing_user["_id"])
        await db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    token, expires_at = create_jwt(user_id, email, hours_valid=18)

    return {"access_token": token, "user_id": user_id, "expires_at": expires_at.isoformat()}
