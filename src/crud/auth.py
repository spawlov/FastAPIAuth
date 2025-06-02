import logging
from datetime import datetime, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError, InvalidHashError
from fastapi import HTTPException
from fastapi.security import HTTPBasic
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from core.models import User, TokenBlacklist

logger = logging.getLogger(__name__)

security = HTTPBasic()
ph = PasswordHasher()


def verify_password(
    hashed_password: str | bytes,
    plain_password: str | bytes,
) -> bool:
    try:
        ph.verify(hashed_password, plain_password.encode("utf-8"))
    except (
        InvalidHashError,
        VerifyMismatchError,
        VerificationError,
    ):
        return False
    return True


def _validate_user_active(user: User) -> None:
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled (not active)",
        )


async def get_auth_user(
    session: AsyncSession,
    username: str,
    password: SecretStr,
) -> User:
    stmt = select(User).where(User.nickname == username)
    user = await session.scalar(stmt)

    if not user or not verify_password(str(user.password), password.get_secret_value()):
        logger.warning(f"Invalid login attempt for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    _validate_user_active(user)

    return user


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User:
    stmt = select(User).where(User.id == user_id)
    user = await session.scalar(stmt)
    if not user:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    _validate_user_active(user)
    return user


async def create_jwt_record(
    session: AsyncSession,
    jti: str,
    user_id: int,
    token_type: str,
    request: Request | None = None,
) -> None:
    jwt_record = TokenBlacklist(
        jti=jti,
        user_id=user_id,
        token_type=token_type,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        created_at=datetime.now(timezone.utc),
    )
    session.add(jwt_record)
    await session.commit()
