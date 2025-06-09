from typing import Any

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth.utils import get_access_token, get_refresh_token


class TestGetJWT:
    @pytest.mark.asyncio
    async def test_get_access_jwt(
        self,
        mocker: MockerFixture,
        session: AsyncSession,
        valid_access_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.create_jwt", return_value="mock.access.jwt")

        result = await get_access_token(
            session,
            valid_access_token_payload,
        )
        assert result == "mock.access.jwt"

    @pytest.mark.asyncio
    async def test_get_refresh_jwt(
        self,
        mocker: MockerFixture,
        session: AsyncSession,
        valid_refresh_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.create_jwt", return_value="mock.refresh.jwt")

        result = await get_refresh_token(
            session,
            valid_refresh_token_payload,
        )
        assert result == "mock.refresh.jwt"
