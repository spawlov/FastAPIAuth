import logging
from datetime import datetime, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBasic
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import TokenBlacklist, User
from core.schemas.auth import TokenType

logger = logging.getLogger(__name__)

# Добавляем кэш для хранения отозванных токенов (заменить на Redis в продакшене)
REVOKED_TOKENS_CACHE = set()

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


async def get_all_users(
    session: AsyncSession,
) -> list[User]:
    stmt = select(User).order_by(User.id)
    users = await session.scalars(stmt)
    return list(users)


async def create_jwt_record(
    session: AsyncSession,
    jti: str,
    user_id: int,
    token_type: TokenType,
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


async def is_token_revoked(
    session: AsyncSession,
    token_jti: str,
) -> bool:
    if token_jti in REVOKED_TOKENS_CACHE:
        return True
    stmt = select(TokenBlacklist).where(TokenBlacklist.jti == token_jti)
    blacklisted = await session.scalar(stmt)
    if blacklisted and blacklisted.reason:
        return True
    return False


async def revoke_token(
    session: AsyncSession,
    token_jti: str,
    reason: str = "user_logout",
) -> None:
    stmt = select(TokenBlacklist).where(TokenBlacklist.jti == token_jti)
    token = await session.scalar(stmt)
    if not token:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token(s) not found",
        )
    token.reason = reason
    token.revoked_at = datetime.now(timezone.utc)
    await session.commit()
    REVOKED_TOKENS_CACHE.add(token_jti)


async def revoke_all_user_tokens(
    session: AsyncSession,
    user_id: int,
    reason: str = "user_logout",
) -> None:
    stmt = select(TokenBlacklist).where(TokenBlacklist.user_id == user_id)
    tokens = await session.scalars(stmt)
    if not tokens:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tokens not found",
        )
    for token in tokens:
        token.reason = reason
        token.revoked_at = datetime.now(timezone.utc)
        REVOKED_TOKENS_CACHE.add(token.jti)
    await session.commit()
