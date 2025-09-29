router = APIRouter()

@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    """
    Returns the current logged-in user's info.
    `current_user` comes from the JWT middleware.
    """
    user_doc = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        name=user_doc["name"],
        profile_picture=user_doc.get("profile_picture"),
        created_at=user_doc["created_at"],
        last_login=user_doc["last_login"]
    )
