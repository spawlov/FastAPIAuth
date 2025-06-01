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
    private_key: str = settings.auth_jwt.private_key,
    algorithm: str = settings.auth_jwt.algorithm,
    expires_in: timedelta = timedelta(minutes=settings.auth_jwt.exp_minutes),
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
