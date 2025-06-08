from typing import Any

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.api_v1.auth.utils import get_user_id


class TestGetUserId:
    @pytest.mark.asyncio
    async def test_get_user_id(
        self,
        mocker,
        session: AsyncSession,
        valid_access_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.is_token_revoked", return_value=False)

        user_id = await get_user_id(session, valid_access_token_payload, "access")
        assert user_id == 1

    @pytest.mark.asyncio
    async def test_get_user_with_revoked_token(
        self,
        mocker,
        session: AsyncSession,
        valid_access_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.is_token_revoked", return_value=True)

        with pytest.raises(HTTPException) as exc:
            await get_user_id(session, valid_access_token_payload, "access")
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc.value.detail == "Token revoked"

    @pytest.mark.asyncio
    async def test_get_user_with_wrong_token_type(
        self,
        mocker,
        session: AsyncSession,
        valid_refresh_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.is_token_revoked", return_value=False)

        with pytest.raises(HTTPException) as exc:
            await get_user_id(session, valid_refresh_token_payload, "access")
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == "Invalid token type: 'refresh', expected 'access'"
