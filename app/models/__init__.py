from app.models.base import Base
from app.models.user import User, Role
from app.models.trail import TrailSection
from app.models.poi import PointOfInterest, POIType
from app.models.post import Post, PostLike

# This file exports all models to ensure they are registered properly
# with SQLAlchemy Base.metadata.
