import logging
import uuid
from datetime import timedelta, datetime, timezone
from typing import Any

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from starlette import status

from core.settings import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    settings.auth_jwt.token_url,
)


def encode_jwt(
    payload: dict[str, Any],
    expires_in: timedelta,
    private_key: str = settings.auth_jwt.private_key,
    algorithm: str = settings.auth_jwt.algorithm,
) -> str:
    to_encode = payload.copy()
    to_encode.update(
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc) + expires_in,
        jti=str(uuid.uuid4()),
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


def create_jwt(type_token: str, token_payload: dict[str, Any], expires: int) -> str:
    jwt_payload = {
        "type": type_token,
    }
    jwt_payload.update(token_payload)
    expire_in = timedelta(minutes=expires)
    return encode_jwt(
        jwt_payload,
        expires_in=expire_in,
    )


def get_access_token(jwt_payload: dict[str, Any]) -> str:
    return create_jwt(
        type_token="access",
        token_payload=jwt_payload,
        expires=settings.auth_jwt.access_exp_minutes,
    )


def get_refresh_token(jwt_payload: dict[str, Any]) -> str:
    payload: dict[str, Any] = {
        "sub": jwt_payload["sub"],
    }
    return create_jwt(
        type_token="refresh",
        token_payload=payload,
        expires=settings.auth_jwt.refresh_exp_minutes,
    )


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
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


def get_user_id(
    token_payload: dict[str, Any],
    expect_token_type: str,
) -> int:
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
