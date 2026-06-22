from datetime import datetime
import enum
import uuid
from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    clerkId = Column(String, unique=True, nullable=True)
    role = Column(Enum(Role, name="Role"), default=Role.USER)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
