# app/schemas/user.py
import uuid
from fastapi_users import schemas
from typing import Optional

class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(schemas.BaseUserCreate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None