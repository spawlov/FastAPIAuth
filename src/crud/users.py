from argon2 import PasswordHasher
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.models import User
from core.schemas.users import UserCreate

ph = PasswordHasher()


async def create_user(
    session: AsyncSession,
    user_create: UserCreate,
) -> User:
    user_data = user_create.model_dump()
    user_data["password"] = ph.hash(user_data["password"])
    try:
        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError as err:
        await session.rollback()
        if "nickname" in str(err.args).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this nickname already exists",
            )
        elif "email" in str(err.args).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create user",
        )
    return user
