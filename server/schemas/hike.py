from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional

class GPSPoint(BaseModel):
    lat: float
    lng: float
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {"lat": 51.5074, "lng": -0.1278, "timestamp": "2025-09-29T13:42:01Z"}
        }

class HikeCreate(BaseModel):
    title: str
    start_time: datetime
    path: list[GPSPoint]

    class Config:
        schema_extra = {
            "example": {
                "title": "Morning Walk",
                "start_time": "2025-09-29T13:42:01Z",
                "path": [
                    {"lat": 51.5074, "lng": -0.1278, "timestamp": "2025-09-29T13:42:01Z"}
                ]
            }
        }

class HikeUpdate(BaseModel):
    end_time: Optional[datetime] = None
    path: Optional[List[GPSPoint]] = None  

    class Config:
        schema_extra = {
            "example": {
                "end_time": "2025-09-29T15:30:00Z",
                "path": [
                    {"lat": 51.5078, "lng": -0.1282, "timestamp": "2025-09-29T11:59:00Z"}
                ]
            }
        }


class HikeOut(BaseModel):
    id: str
    title: str
    start_time: datetime
    end_time: datetime | None
    distance_km: float
    path: list[GPSPoint]
    cheers: list

    class Config:
        schema_extra = {
            "example": {
                "id": "68da8ca9de8c84d77af2e156",
                "title": "Morning Walk",
                "start_time": "2025-09-29T13:42:01Z",
                "end_time": None,
                "distance_km": 0.05,
                "path": [{"lat": 51.5074, "lng": -0.1278, "timestamp": "2025-09-29T13:42:01Z"}],
                "cheers": []
            }
        }