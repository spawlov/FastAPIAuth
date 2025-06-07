import logging
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.schemas.auth import TokenType
from core.settings import settings
from crud.auth import create_jwt_record, is_token_revoked

logger = logging.getLogger(__name__)

# Простой in-memory rate limiter (использовать Redis)
RATE_LIMIT_DATA = {}

oauth2_scheme = OAuth2PasswordBearer(
    settings.auth_jwt.token_url,
)


def encode_jwt(
    payload: dict[str, Any],
    expires_in: timedelta,
    jti: str,
    private_key: str = settings.auth_jwt.private_key,
    algorithm: str = settings.auth_jwt.algorithm,
) -> str:
    to_encode = payload.copy()
    to_encode.update(
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc) + expires_in,
        jti=jti,
    )
    jwt_encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm,
    )
    return jwt_encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key,
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict[str, Any]:
    jwt_decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return jwt_decoded


async def create_jwt(
    session: AsyncSession,
    token_type: TokenType,
    token_payload: dict[str, Any],
    expires: int,
    request: Request | None = None,
) -> str:
    jwt_payload = {
        "type": token_type,
    }
    jwt_payload.update(token_payload)
    expire_in = timedelta(minutes=expires)
    jti = str(uuid.uuid4())
    await create_jwt_record(
        session=session,
        jti=jti,
        user_id=token_payload["sub"],
        token_type=token_type,
        request=request,
    )
    return encode_jwt(
        jwt_payload,
        expires_in=expire_in,
        jti=jti,
    )


async def get_access_token(
    session: AsyncSession,
    jwt_payload: dict[str, Any],
    request: Request | None = None,
) -> str:
    return await create_jwt(  # noqa
        session=session,
        token_type="access",
        token_payload=jwt_payload,
        expires=settings.auth_jwt.access_exp_minutes,
        request=request,
    )


async def get_refresh_token(
    session: AsyncSession,
    jwt_payload: dict[str, Any],
    request: Request | None = None,
) -> str:
    payload: dict[str, Any] = {
        "sub": jwt_payload["sub"],
    }
    return await create_jwt(  # noqa
        session=session,
        token_type="refresh",
        token_payload=payload,
        expires=settings.auth_jwt.refresh_exp_minutes,
        request=request,
    )


def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict[str, Any]:
    try:
        payload = decode_jwt(token)
    except InvalidTokenError as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
    return payload


async def get_user_id(
    session: AsyncSession,
    token_payload: dict[str, Any],
    expect_token_type: TokenType,
) -> int:
    if not token_payload or not isinstance(token_payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No token_payload provided or wrong token_payload type",
        )
    if await is_token_revoked(session, token_payload.get("jti")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token revoked",
        )
    if (current_token_type := token_payload.get("type")) != expect_token_type:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type: {current_token_type!r}, expected {expect_token_type!r}",
        )
    if not (user_id := token_payload.get("sub")):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return int(user_id)


def rate_limited(max_calls: int, time_frame: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            request: Request,
            session: AsyncSession,
            form_data: OAuth2PasswordRequestForm,
        ):
            client_ip = request.client.host
            now = datetime.now()
            requests_data = RATE_LIMIT_DATA.get(client_ip, [])
            requests_data = [t for t in requests_data if now - t < timedelta(seconds=time_frame)]

            if len(requests_data) >= max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Try again later.",
                )

            requests_data.append(now)
            RATE_LIMIT_DATA[client_ip] = requests_data

            return await func(request, session, form_data)

        return wrapper

    return decorator
