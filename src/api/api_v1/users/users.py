from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper
from core.schemas.users import UserCreate, UserRead
from crud import users as crud_users

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    user: UserCreate,
):
    return await crud_users.create_user(session, user)
