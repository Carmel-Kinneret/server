from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.poi import PointOfInterest as POIModel, POIType
from app.schemas.poi import POI as POISchema

router = APIRouter()

@router.get("", response_model=List[POISchema])
async def read_pois(
    type: Optional[POIType] = Query(None, description="Filter POIs by type (MAIN or EVENT)"),
    db: AsyncSession = Depends(get_db)
):
    query = select(POIModel).where(POIModel.isActive == True)
    if type:
        query = query.where(POIModel.type == type)
    
    result = await db.execute(query)
    pois = result.scalars().all()
    return pois
