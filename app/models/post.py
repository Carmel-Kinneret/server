import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, JSON, func, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base

class Post(Base):
    __tablename__ = "post"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    imageUrl = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    geojson = Column(JSON, nullable=False)  # Stores the geojson Point
    isActive = Column(Boolean, default=True, nullable=False)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    user = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")

class PostLike(Base):
    __tablename__ = "postLike"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    postId = Column(String, ForeignKey("post.id", ondelete="CASCADE"), nullable=False)
    createdAt = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
