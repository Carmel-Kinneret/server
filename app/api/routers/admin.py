from fastapi import APIRouter, Depends, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.post import Post as PostModel
from app.models.poi import PointOfInterest as POIModel
from app.schemas.post import Post as PostSchema, PostUpdate
from app.schemas.poi import POI as POISchema, POICreate, POIUpdate
from app.core.auth import get_current_admin
from app.core.exceptions import NotFoundException

router = APIRouter(dependencies=[Depends(get_current_admin)])

@router.delete("/posts/{postId}", response_model=PostSchema)
async def admin_delete_post(
    postId: str = Path(...), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(PostModel).where(PostModel.id == postId))
    post = result.scalars().first()
    if not post:
        raise NotFoundException(message="Resource not found or has been removed.")
    await db.delete(post)
    await db.commit()
    return post
async def admin_update_post(
    postId: str = Path(...),
    post_update: PostUpdate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(PostModel).where(PostModel.id == postId))
    post = result.scalars().first()
    if not post:
        raise NotFoundException(message="Resource not found or has been removed.")
        
    if post_update.isActive is not None:
        post.isActive = post_update.isActive
        
    await db.commit()
    await db.refresh(post)
    
    # Needs hasLiked field (defaults to False for admin view or needs resolution)
    post.hasLiked = False
    return post

@router.patch("/pois/{poiId}", response_model=POISchema)
async def admin_update_poi(
    poiId: str = Path(...),
    poi_update: POIUpdate = Body(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(POIModel).where(POIModel.id == poiId))
    poi = result.scalars().first()
    if not poi:
        raise NotFoundException(message="Resource not found or has been removed.")
        
    if poi_update.title is not None:
        poi.title = poi_update.title
    if poi_update.type is not None:
        poi.type = poi_update.type
    if poi_update.imageUrl is not None:
        poi.imageUrl = poi_update.imageUrl
    if poi_update.geojson is not None:
        poi.geojson = poi_update.geojson
    if poi_update.metadata is not None:
        poi.metadata = poi_update.metadata
    if poi_update.isActive is not None:
        poi.isActive = poi_update.isActive
        
    await db.commit()
    await db.refresh(poi)
    return poi

@router.post("/pois", response_model=POISchema)
async def admin_create_poi(
    poi_in: POICreate,
    db: AsyncSession = Depends(get_db)
):
    geojson = poi_in.geojson
    
    db_poi = POIModel(
        title=poi_in.title,
        type=poi_in.type,
        imageUrl=poi_in.imageUrl,

        geojson=geojson,
        metadata=poi_in.metadata,
        isActive=True
    )
    
    db.add(db_poi)
    await db.commit()
    await db.refresh(db_poi)
    return db_poi

@router.delete("/pois/{poiId}", response_model=POISchema)
async def admin_delete_poi(poiId: str = Path(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(POIModel).where(POIModel.id == poiId))
    poi = result.scalars().first()
    if not poi:
        raise NotFoundException(message="Resource not found or has been removed.")
    await db.delete(poi)
    await db.commit()
    return poi

