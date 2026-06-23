from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from app.models.base import Base

class TrailSection(Base):
    __tablename__ = "trailSection"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    geojson = Column(JSON, nullable=False)  # Stores the geojson LineString
    orderIndex = Column(Integer, nullable=False)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now(), nullable=True)
