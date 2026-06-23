"""Posts router with enhanced validation and search capabilities.

- Enforces that a new post must be within 1 km of the nearest POI.
- Provides a `/search` endpoint that accepts a location and a sorting enum
  (distance, recent, most liked).
- Secures the user-posts endpoint so a user can only fetch their own posts.
"""

# Standard library imports
from fastapi import Path
from pydantic import BaseModel
import math
from enum import Enum

# Third‑party imports
from fastapi import APIRouter, Depends, Query, HTTPException, status
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

# Local imports
from app.db.database import get_db
from app.models.user import User as UserModel
from app.models.post import Post as PostModel, PostLike as PostLikeModel
from app.models.poi import PointOfInterest as POIModel
from app.schemas.post import (
    Post as PostSchema,
    PostCreate,
    PostListResponse,
    PostLikeResponse,
)
from app.core.auth import get_current_user, get_optional_current_user
from app.core.exceptions import NotFoundException

router = APIRouter()

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Return distance in meters between two (lon, lat) points.

    Uses the haversine formula; suitable for short distances like the 1 km rule.
    """
    R = 6371000  # Earth radius in metres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def extract_point(geojson: dict) -> tuple[float, float]:
    """Extract ``(lon, lat)`` from a GeoJSON ``Point`` object.

    Expected shape: ``{"type": "Point", "coordinates": [lon, lat]}``.
    """
    coords = geojson.get("coordinates", [])
    if len(coords) != 2:
        raise ValueError("Invalid GeoJSON Point coordinates")
    return coords[0], coords[1]


class PostSortEnum(str, Enum):
    distance = "distance"
    recent = "recent"
    popular = "popular"


# PostSearchRequest removed – no longer needed after eliminating the search endpoint

# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=PostListResponse)
async def read_posts(
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    sort_by: PostSortEnum = Query(PostSortEnum.recent),
    location: Optional[str] = Query(None, description="GeoJSON Point (as JSON string) for distance sorting"),
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostListResponse:
    """Return a paginated list of active posts sorted according to the provided sort option.

    * ``recent`` – newest posts first (default)
    * ``popular`` – posts with the most likes first
    * ``distance`` – requires a GeoJSON ``location`` query parameter (as a JSON string) and sorts by proximity.
    """
    if sort_by == PostSortEnum.distance:
        if not location:
            raise HTTPException(
                status_code=400,
                detail="GeoJSON location must be provided for distance sorting",
            )
        try:
            user_point = json.loads(location)
            user_lon, user_lat = extract_point(user_point)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid GeoJSON location format",
            )

    # Fetch all active posts
    base_query = select(PostModel).where(PostModel.isActive == True)
    result = await db.execute(base_query)
    all_posts = list(result.scalars().all())

    # Pre‑compute like counts and distances (if needed)
    like_counts: dict[str, int] = {}
    distances: dict[str, float] = {}
    for p in all_posts:
        cnt_res = await db.execute(select(func.count(PostLikeModel.id)).where(PostLikeModel.postId == p.id))
        like_counts[p.id] = cnt_res.scalar() or 0
        if sort_by == PostSortEnum.distance:
            try:
                lon, lat = extract_point(p.geojson)
                distances[p.id] = haversine(user_lon, user_lat, lon, lat)
            except Exception:
                distances[p.id] = float("inf")

    # Apply sorting according to ``sort_by``
    if sort_by == PostSortEnum.recent:
        sorted_posts = sorted(all_posts, key=lambda p: p.createdAt, reverse=True)
    elif sort_by == PostSortEnum.popular:
        sorted_posts = sorted(all_posts, key=lambda p: like_counts[p.id], reverse=True)
    else:  # distance
        sorted_posts = sorted(all_posts, key=lambda p: distances[p.id])


    # Pagination
    paginated = sorted_posts[offset : offset + limit + 1]
    has_next = len(paginated) > limit
    posts = paginated[:limit] if has_next else paginated
    next_offset = offset + limit if has_next else None

    # Attach ``hasLiked`` flag when a user is authenticated
    if current_user:
        post_ids = [p.id for p in posts]
        likes_res = await db.execute(
            select(PostLikeModel.postId).where(
                PostLikeModel.userId == current_user.id,
                PostLikeModel.postId.in_(post_ids),
            )
        )
        liked_ids = set(likes_res.scalars().all())
        for p in posts:
            p.hasLiked = p.id in liked_ids
    else:
        for p in posts:
            p.hasLiked = False

    return PostListResponse(posts=posts, next_offset=next_offset)


@router.post("/", response_model=PostSchema)
async def create_post(
    post_in: PostCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new post.

    The post must be within **1 km** of the nearest active POI.
    """
    # Extract location from the supplied GeoJSON
    try:
        post_lon, post_lat = extract_point(post_in.geojson)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid post geojson payload") from exc

    # Find the closest POI
    poi_res = await db.execute(select(POIModel).where(POIModel.isActive == True))
    pois = poi_res.scalars().all()
    if not pois:
        raise HTTPException(status_code=400, detail="No POIs available for distance validation")
    min_distance = min(
        haversine(post_lon, post_lat, *extract_point(p.geojson)) for p in pois
    )
    if min_distance > 1000:  # meters
        raise HTTPException(
            status_code=400,
            detail="Post location exceeds 1 km from the nearest point of interest",
        )

    db_post = PostModel(
        userId=current_user.id,
        imageUrl=post_in.imageUrl,
        caption=post_in.caption,
        geojson=post_in.geojson,
        isActive=True,
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    db_post.hasLiked = False
    return db_post


@router.get("/users/{userId}/posts", response_model=List[PostSchema])
async def read_user_posts(
    userId: str = Path(...),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return posts for a specific user.

    The ``userId`` must match the authenticated user; otherwise a *403* error is raised.
    """
    if not current_user or current_user.id != userId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only access your own posts",
        )
    query = (
        select(PostModel)
        .where(PostModel.userId == userId, PostModel.isActive == True)
        .order_by(PostModel.createdAt.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = list(result.scalars().all())
    # Attach ``hasLiked`` information
    if current_user:
        post_ids = [p.id for p in posts]
        likes_res = await db.execute(
            select(PostLikeModel.postId).where(
                PostLikeModel.userId == current_user.id,
                PostLikeModel.postId.in_(post_ids),
            )
        )
        liked_ids = set(likes_res.scalars().all())
        for p in posts:
            p.hasLiked = p.id in liked_ids
    else:
        for p in posts:
            p.hasLiked = False
    return posts


# POST /search endpoint removed as per user request


@router.post("/{postId}/like", response_model=PostLikeResponse)
async def like_post(
    postId: str = Path(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Like a post; creates a ``PostLike`` if it does not already exist."""
    post_result = await db.execute(
        select(PostModel).where(PostModel.id == postId, PostModel.isActive == True)
    )
    post = post_result.scalars().first()
    if not post:
        raise NotFoundException(message="Resource not found or has been removed.")
    like_result = await db.execute(
        select(PostLikeModel).where(
            PostLikeModel.postId == postId,
            PostLikeModel.userId == current_user.id,
        )
    )
    like = like_result.scalars().first()
    if not like:
        like = PostLikeModel(postId=postId, userId=current_user.id)
        db.add(like)
        await db.commit()
    count_res = await db.execute(
        select(func.count(PostLikeModel.id)).where(PostLikeModel.postId == postId)
    )
    total_likes = count_res.scalar() or 0
    return PostLikeResponse(success=True, totalLikes=total_likes)


@router.delete("/{postId}/like", response_model=PostLikeResponse)
async def unlike_post(
    postId: str = Path(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a like from a post if it exists."""
    post_result = await db.execute(
        select(PostModel).where(PostModel.id == postId, PostModel.isActive == True)
    )
    post = post_result.scalars().first()
    if not post:
        raise NotFoundException(message="Resource not found or has been removed.")
    like_result = await db.execute(
        select(PostLikeModel).where(
            PostLikeModel.postId == postId,
            PostLikeModel.userId == current_user.id,
        )
    )
    like = like_result.scalars().first()
    if like:
        await db.delete(like)
        await db.commit()
    count_res = await db.execute(
        select(func.count(PostLikeModel.id)).where(PostLikeModel.postId == postId)
    )
    total_likes = count_res.scalar() or 0
    return PostLikeResponse(success=True, totalLikes=total_likes)
