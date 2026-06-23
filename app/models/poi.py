import enum
import uuid
from sqlalchemy import Column, String, Enum, Float, Boolean, DateTime, JSON, func
from app.models.base import Base

class POIType(str, enum.Enum):
    MAIN = "MAIN"
    EVENT = "EVENT"

class PointOfInterest(Base):
    __tablename__ = "pointOfInterest"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    type = Column(Enum(POIType, name="POIType"), nullable=False, default=POIType.MAIN)
    imageUrl = Column(String, nullable=True)
    geojson = Column(JSON, nullable=False)  # Stores the geojson Point
    poi_metadata = Column("metadata", JSON, nullable=True, default=dict)  # Mapped to 'metadata' column to avoid SQLAlchemy namespace conflict
    isActive = Column(Boolean, default=True, nullable=False)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now(), nullable=True)


