import logging
from typing import (
    Annotated,
    Any,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.models.db_helper import db_helper
from core.schemas.auth import TokenInfo, AuthUser
from crud.auth import get_auth_user, get_user_by_id
from .utils import (
    encode_jwt,
    get_current_token_payload,
    get_access_token,
    get_refresh_token,
    create_jwt,
)


logger = logging.getLogger(__name__)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(dependencies=[Depends(http_bearer)])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def login(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenInfo:
    user = await get_auth_user(
        session,
        form_data.username,
        SecretStr(form_data.password),
    )
    jwt_payload = {
        "sub": str(user.id),
        "username": user.nickname,
    }
    access_token = get_access_token(jwt_payload)
    refresh_token = get_refresh_token(jwt_payload)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def refresh_jwt(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    refresh_payload: Annotated[dict[str, Any], Depends(get_current_token_payload)],
) -> TokenInfo:
    if (current_token_type := refresh_payload.get("type")) != "refresh":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type: {current_token_type!r}, expected 'refresh'",
        )
    user_id = refresh_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = await get_user_by_id(session, user_id)
    jwt_payload = {
        "sub": str(user.id),
        "username": user.nickname,
    }
    access_token = get_access_token(jwt_payload)
    return TokenInfo(
        access_token=access_token,
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=AuthUser,
    response_model_exclude={"id", "password"},
    response_model_exclude_none=True,
)
async def me(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    access_payload: Annotated[dict[str, Any], Depends(get_current_token_payload)],
) -> AuthUser:
    if (current_token_type := access_payload.get("type")) != "access":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type: {current_token_type!r}, expected 'access'",
        )
    user_id = access_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = await get_user_by_id(session, user_id)
    return AuthUser.model_validate(user)
