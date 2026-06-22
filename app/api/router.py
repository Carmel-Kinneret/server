from fastapi import APIRouter
from app.api.routers import users, trails, pois, posts, admin

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(trails.router, prefix="/trails", tags=["trails"])
api_router.include_router(pois.router, prefix="/pois", tags=["pois"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
