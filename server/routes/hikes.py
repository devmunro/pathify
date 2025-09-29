from fastapi import APIRouter, Depends, HTTPException
from db import db
from utils.jwt_utils import get_current_user
from schemas.hike import HikeCreate, HikeUpdate, HikeOut, GPSPoint
from bson import ObjectId
from datetime import datetime, timezone
from typing import List
import math

router = APIRouter()


# -----------------------------
# Helper: Calculate distance between two GPS points (km)
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def calculate_distance(path: List[GPSPoint]) -> float:
    distance = 0.0
    for i in range(1, len(path)):
        distance += haversine(path[i-1].lat, path[i-1].lng, path[i].lat, path[i].lng)
    return distance


# -----------------------------
# Create a new hike
# -----------------------------
@router.post("/hikes")
async def create_hike(hike: HikeCreate, current_user=Depends(get_current_user)):
    """
    Create a new hike for the logged-in user.

    Args:
        hike (HikeCreate): Data for the hike including optional title, start_time, and initial GPS path.
        current_user (dict, Depends): The currently authenticated user extracted from JWT.

    Returns:
        dict: Contains the newly created hike's ID.
    """
    now_utc = datetime.now(timezone.utc)

    # Validate GPS points
    for p in hike.path:
        if not (-90 <= p.lat <= 90) or not (-180 <= p.lng <= 180):
            raise HTTPException(status_code=400, detail="Invalid GPS coordinates")

    distance_km = calculate_distance(hike.path)

    result = await db.hikes.insert_one({
        "user_id": ObjectId(current_user["user_id"]),
        "title": hike.title,
        "start_time": hike.start_time,
        "end_time": None,
        "path": [p.model_dump() for p in hike.path],
        "cheers": [],
        "distance_km": distance_km,
        "created_at": now_utc
    })
    return {"hike_id": str(result.inserted_id)}


# -----------------------------
# Update an existing hike
# -----------------------------
@router.put("/hikes/{hike_id}")
async def update_hike(hike_id: str, hike: HikeUpdate, current_user=Depends(get_current_user)):
    """
    Update an existing hike for the logged-in user.
    Can append new GPS points and/or set the hike's end_time.

    Args:
        hike_id (str): The MongoDB ID of the hike to update.
        hike (HikeUpdate): Fields to update, including optional end_time and path points.
        current_user (dict, Depends): The currently authenticated user extracted from JWT.

    Raises:
        HTTPException: 400 if no valid fields are provided.
        HTTPException: 404 if the hike does not exist for the current user.

    Returns:
        dict: Status message indicating the hike was updated.
    """
    update_data = {}
    push_data = {}

    if hike.end_time:
        update_data["end_time"] = hike.end_time
    if hike.path:
        # Validate GPS points
        for p in hike.path:
            if not (-90 <= p.lat <= 90) or not (-180 <= p.lng <= 180):
                raise HTTPException(status_code=400, detail="Invalid GPS coordinates")
        push_data["path"] = {"$each": [p.model_dump() for p in hike.path]}

    if not update_data and not push_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    update_query = {}
    if update_data:
        update_query["$set"] = update_data
    if push_data:
        update_query["$push"] = push_data

    # Update hike
    result = await db.hikes.update_one(
        {"_id": ObjectId(hike_id), "user_id": ObjectId(current_user["user_id"])},
        update_query
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Hike not found")

    # Recalculate distance if new path points were added
    if hike.path:
        hike_doc = await db.hikes.find_one({"_id": ObjectId(hike_id)})
        total_distance = calculate_distance([GPSPoint(**p) for p in hike_doc["path"]])
        await db.hikes.update_one(
            {"_id": ObjectId(hike_id)},
            {"$set": {"distance_km": total_distance}}
        )

    return {"status": "updated"}


# -----------------------------
# Get all hikes for current user
# -----------------------------
@router.get("/hikes", response_model=List[HikeOut])
async def get_my_hikes(current_user=Depends(get_current_user)):
    """
    Retrieve all hikes for the logged-in user.

    Args:
        current_user (dict, Depends): The currently authenticated user extracted from JWT.

    Returns:
        List[HikeOut]: A list of all hikes for the user, including
        start_time, end_time, path, distance_km, and cheers.
    """
    hikes_cursor = db.hikes.find({"user_id": ObjectId(current_user["user_id"])})
    hikes = []
    async for hike in hikes_cursor:
        hike["id"] = str(hike["_id"])  # Convert ObjectId to string
        hike.setdefault("distance_km", 0.0)
        hike.setdefault("path", [])
        hike.setdefault("cheers", [])
        hikes.append(HikeOut(**hike))
    return hikes
