from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db as get_async_session
from sqlalchemy import select, text
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.get("/", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    print(result)
    users = result.fetchall()
    return [UserRead.from_orm(u) for u in users]

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, session: AsyncSession = Depends(get_async_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_async_session)):
    user = User(**payload.dict())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.from_orm(user)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, payload: UserUpdate, session: AsyncSession = Depends(get_async_session)):
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
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
    return None
