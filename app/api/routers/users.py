from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_async_session

from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.get("/", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_async_session)):
    """Retrieve all users."""
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [UserRead.from_orm(u) for u in users]

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, session: AsyncSession = Depends(get_async_session)):
    """Retrieve a single user by ID."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_async_session)):
    """Create a new user."""
    payload_dict = payload.dict()
    if "role" in payload_dict and payload_dict["role"] is not None:
        payload_dict["role"] = payload_dict["role"].value
    user = User(**payload_dict)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.from_orm(user)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, payload: UserUpdate, session: AsyncSession = Depends(get_async_session)):
    """Update an existing user."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return UserRead.from_orm(user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, session: AsyncSession = Depends(get_async_session)):
    """Delete a user."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
    return None
