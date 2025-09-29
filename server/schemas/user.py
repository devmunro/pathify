from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserOut(BaseModel):
    id: str
    email: str
    name: str
    profile_picture: Optional[str]
    created_at: datetime
    last_login: datetime
