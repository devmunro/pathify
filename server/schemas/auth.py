from pydantic import BaseModel

class GoogleLoginSchema(BaseModel):
    id_token: str
