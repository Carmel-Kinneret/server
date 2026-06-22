from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class TrailSectionBase(BaseModel):
    name: str
    geoJson: Dict[str, Any]  # Store LineString GeoJSON object
    orderIndex: int

class TrailSectionCreate(TrailSectionBase):
    pass

class TrailSectionUpdate(BaseModel):
    name: Optional[str] = None
    geoJson: Optional[Dict[str, Any]] = None
    orderIndex: Optional[int] = None

class TrailSectionInDB(TrailSectionBase):
    id: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TrailSection(TrailSectionInDB):
    pass
