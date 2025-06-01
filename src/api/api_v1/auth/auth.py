from typing import (
    Annotated,
    Any,
)

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.models.db_helper import db_helper
from core.schemas.auth import TokenInfo, AuthUser
from crud.auth import get_auth_user, get_user_by_id
from .utils import (
    encode_jwt,
    get_current_token_payload,
)

router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenInfo)
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
    token = encode_jwt(jwt_payload)

    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=AuthUser,
    response_model_exclude={"id", "password"},
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def me(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    jwt_payload: Annotated[dict[str, Any], Depends(get_current_token_payload)],
) -> AuthUser:
    user_id = jwt_payload["sub"]
    user = await get_user_by_id(session, user_id)
    return AuthUser.model_validate(user)
