from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from db import db
from schemas.user import UserOut
from utils.jwt_utils import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    """
    Returns the current logged-in user's info.
    `current_user` is extracted from the JWT token.
    """
    # Ensure ObjectId conversion
    try:
        user_id = ObjectId(current_user["user_id"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user_doc = await db.users.find_one({"_id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut(
        id=str(user_doc["_id"]),
        email=user_doc.get("email"),
        name=user_doc.get("name"),
        profile_picture=user_doc.get("profile_picture"),
        created_at=user_doc.get("created_at"),
        last_login=user_doc.get("last_login")
    )
