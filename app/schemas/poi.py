"""Pydantic schemas for Point of Interest (POI) objects.

These schemas handle validation and serialization for POI data.
All spatial information is stored in the ``geojson`` field.
"""

# Standard library imports
from datetime import datetime

# Third‑party imports
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

# Local imports
from app.models.poi import POIType


class POIBase(BaseModel):
    """Base fields shared by POI creation and update schemas."""

    title: str
    type: POIType
    imageUrl: Optional[str] = None
    geojson: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("geojson", "poi_geojson"),
        serialization_alias="geojson",
    )


class POICreate(POIBase):
    """Schema for creating a new POI.

    ``geojson`` is required for creation to ensure spatial data is present.
    """

    geojson: Dict[str, Any]


class POIUpdate(BaseModel):
    """Schema for partial updates of a POI.

    All fields are optional; only provided values will be updated.
    """

    title: Optional[str] = None
    type: Optional[POIType] = None
    imageUrl: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("metadata", "poi_metadata"),
        serialization_alias="metadata",
    )
    isActive: Optional[bool] = None


class POIInDB(POIBase):
    """Full POI representation as stored in the database."""

    id: str
    geojson: Dict[str, Any]
    isActive: bool
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class POI(POIInDB):
    """Public POI schema returned by API endpoints (currently identical to ``POIInDB``)."""

    pass
