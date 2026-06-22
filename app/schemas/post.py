from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class PostBase(BaseModel):
    imageUrl: str
    caption: Optional[str] = None
    geojson: Dict[str, Any]
class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    isActive: Optional[bool] = None

class PostInDB(PostBase):
    id: str
    userId: str
    geojson: Dict[str, Any]
    isActive: bool
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Post(PostInDB):
    hasLiked: Optional[bool] = None

class PostListResponse(BaseModel):
    posts: List[Post]
    next_offset: Optional[int] = None

class PostLikeResponse(BaseModel):
    success: bool
    totalLikes: int
