import logging
from typing import (
    Annotated,
    Any,
)

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.models.db_helper import db_helper
from core.schemas.auth import TokenInfo, AuthUser
from crud.auth import (
    get_auth_user,
    get_user_by_id,
    revoke_token,
    revoke_all_user_tokens,
)
from .utils import (
    get_current_token_payload,
    get_access_token,
    get_refresh_token,
    get_user_id,
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
    request: Request,
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
    access_token = await get_access_token(session, jwt_payload, request)
    refresh_token = await get_refresh_token(session, jwt_payload, request)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    access_payload: Annotated[dict[str, Any], Depends(get_current_token_payload)],
    logout_all: bool = False,
) -> dict[str, str]:
    user_id = await get_user_id(session, access_payload, expect_token_type="access")
    if logout_all:
        await revoke_all_user_tokens(
            session=session,
            user_id=user_id,
            reason="user_logout_all",
        )
        message = "All sessions terminated successfully"
    else:
        await revoke_token(
            session=session,
            token_jti=access_payload.get("jti"),
            reason="user_logout",
        )
        message = "Logged out successfully"

    return {
        "message": "success",
        "details": message,
    }


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def refresh_jwt(
    request: Request,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    refresh_payload: Annotated[dict[str, Any], Depends(get_current_token_payload)],
) -> TokenInfo:
    user_id = await get_user_id(session, refresh_payload, expect_token_type="refresh")
    user = await get_user_by_id(session, user_id)
    jwt_payload = {
        "sub": str(user.id),
        "username": user.nickname,
    }
    access_token = await get_access_token(session, jwt_payload, request)
    return TokenInfo(
        access_token=access_token,
    )


@router.post(
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
    user_id = await get_user_id(session, access_payload, expect_token_type="access")
    user = await get_user_by_id(session, user_id)
    return AuthUser.model_validate(user)
