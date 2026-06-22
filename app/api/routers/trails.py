from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.trail import TrailSection as TrailSectionModel
from app.schemas.trail import TrailSection as TrailSectionSchema

router = APIRouter()

@router.get("", response_model=List[TrailSectionSchema])
async def read_trails(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrailSectionModel).order_by(TrailSectionModel.orderIndex))
    trails = result.scalars().all()
    return trails
