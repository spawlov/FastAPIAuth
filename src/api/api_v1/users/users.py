from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper
from core.models.user import User
from core.schemas.users import UserRead, UserCreate
from crud import users as crud_users

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserRead],
    status_code=200,
)
async def get_all_users(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
) -> list[User]:
    return await crud_users.get_all_users(session)


@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_session),
    ],
    user: UserCreate,
):
    return await crud_users.create_user(session, user)
