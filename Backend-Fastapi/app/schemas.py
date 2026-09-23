from pydantic import BaseModel
from fastapi_users import schemas
import uuid

class PostCreate(BaseModel):
    caption: str
    url: str
    file_type: str
    file_name: str

class PostResponse(BaseModel):
    id: str
    caption: str
    url: str
    file_type: str
    file_name: str

    class Config:
        from_attributes = True

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass