from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.post import Post as PostModel, PostLike as PostLikeModel
from app.schemas.post import (
    Post as PostSchema,
    PostCreate,
    PostListResponse,
    PostLikeResponse,
)
from app.core.auth import get_current_user, get_optional_current_user
from app.core.exceptions import NotFoundException

router = APIRouter()

@router.get("", response_model=PostListResponse)
async def read_posts(
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(PostModel).where(PostModel.isActive == True)
    
    if min_lat is not None:
        query = query.where(PostModel.lat >= min_lat)
    if max_lat is not None:
        query = query.where(PostModel.lat <= max_lat)
    if min_lon is not None:
        query = query.where(PostModel.lon >= min_lon)
    if max_lon is not None:
        query = query.where(PostModel.lon <= max_lon)
        
    query = query.order_by(PostModel.createdAt.desc()).offset(offset).limit(limit + 1)
    
    result = await db.execute(query)
    posts = list(result.scalars().all())
    
    has_next = len(posts) > limit
    if has_next:
        posts = posts[:limit]
        next_offset = offset + limit
    else:
        next_offset = None
        
    # Append hasLiked status if authenticated
    if current_user and posts:
        post_ids = [post.id for post in posts]
        likes_result = await db.execute(
            select(PostLikeModel.postId)
            .where(PostLikeModel.userId == current_user.id)
            .where(PostLikeModel.postId.in_(post_ids))
        )
        liked_post_ids = set(likes_result.scalars().all())
        for post in posts:
            post.hasLiked = post.id in liked_post_ids
    else:
        for post in posts:
            post.hasLiked = False
            
    return PostListResponse(posts=posts, next_offset=next_offset)

@router.post("", response_model=PostSchema)
async def create_post(
    post_in: PostCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    geojson = {
        "type": "Point",
        "coordinates": [post_in.lon, post_in.lat]
    }
    
    db_post = PostModel(
        userId=current_user.id,
        imageUrl=post_in.imageUrl,
        caption=post_in.caption,
        lat=post_in.lat,
        lon=post_in.lon,
        geojson=geojson,
        isActive=True
    )
    
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    
    # Newly created post cannot be liked yet
    db_post.hasLiked = False
    return db_post

@router.get("/users/{userId}/posts", response_model=List[PostSchema])
async def read_user_posts(
    userId: str = Path(...),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(PostModel)
        .where(PostModel.userId == userId, PostModel.isActive == True)
        .order_by(PostModel.createdAt.desc())
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(query)
    posts = list(result.scalars().all())
    
    if current_user and posts:
        post_ids = [post.id for post in posts]
        likes_result = await db.execute(
            select(PostLikeModel.postId)
            .where(PostLikeModel.userId == current_user.id)
            .where(PostLikeModel.postId.in_(post_ids))
        )
        liked_post_ids = set(likes_result.scalars().all())
        for post in posts:
            post.hasLiked = post.id in liked_post_ids
    else:
        for post in posts:
            post.hasLiked = False
            
    return posts

@router.post("/{postId}/like", response_model=PostLikeResponse)
async def like_post(
    postId: str = Path(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify post exists and is active
    post_result = await db.execute(
        select(PostModel).where(PostModel.id == postId, PostModel.isActive == True)
    )
    post = post_result.scalars().first()
    if not post:
        raise NotFoundException(message="Resource not found or has been removed.")
        
    # Check if user already liked it
    like_result = await db.execute(
        select(PostLikeModel).where(
            PostLikeModel.postId == postId,
            PostLikeModel.userId == current_user.id
        )
    )
    like = like_result.scalars().first()
    
    if not like:
        like = PostLikeModel(postId=postId, userId=current_user.id)
        db.add(like)
        await db.commit()
        
    # Count total likes
    count_result = await db.execute(
        select(func.count(PostLikeModel.id)).where(PostLikeModel.postId == postId)
    )
    total_likes = count_result.scalar() or 0
    
    return PostLikeResponse(success=True, totalLikes=total_likes)

@router.delete("/{postId}/like", response_model=PostLikeResponse)
async def unlike_post(
    postId: str = Path(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify post exists and is active
    post_result = await db.execute(
        select(PostModel).where(PostModel.id == postId, PostModel.isActive == True)
    )
    post = post_result.scalars().first()
    if not post:
        raise NotFoundException(message="Resource not found or has been removed.")
        
    # Find the like
    like_result = await db.execute(
        select(PostLikeModel).where(
            PostLikeModel.postId == postId,
            PostLikeModel.userId == current_user.id
        )
    )
    like = like_result.scalars().first()
    
    if like:
        await db.delete(like)
        await db.commit()
        
    # Count total likes
    count_result = await db.execute(
        select(func.count(PostLikeModel.id)).where(PostLikeModel.postId == postId)
    )
    total_likes = count_result.scalar() or 0
    
    return PostLikeResponse(success=True, totalLikes=total_likes)
