from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.user import Role

class UserBase(BaseModel):
    userName: str
    clerkId: Optional[str] = None
    role: Role = Role.USER

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    userName: Optional[str] = None
    role: Optional[Role] = None

class UserInDBBase(UserBase):
    id: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    pass
class UserRead(UserInDBBase):
    """Schema used for responses - includes all DB fields"""
    pass
