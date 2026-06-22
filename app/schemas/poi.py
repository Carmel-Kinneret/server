from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from app.models.poi import POIType

class POIBase(BaseModel):
    title: str
    type: POIType
    imageUrl: Optional[str] = None
    lat: float
    lon: float
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("metadata", "poi_metadata"),
        serialization_alias="metadata"
    )

class POICreate(POIBase):
    pass

class POIUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[POIType] = None
    imageUrl: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        validation_alias=AliasChoices("metadata", "poi_metadata"),
        serialization_alias="metadata"
    )
    isActive: Optional[bool] = None

class POIInDB(POIBase):
    id: str
    geoJson: Dict[str, Any]
    isActive: bool
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class POI(POIInDB):
    pass
