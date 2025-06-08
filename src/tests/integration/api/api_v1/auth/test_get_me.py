from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient

from core.models import User


class TestMe:
    @pytest.mark.asyncio
    async def test_me_success(
        self,
        mocker,
        async_client: AsyncClient,
        valid_access_token_payload: dict[str, Any],
        mock_user: User,
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.decode_jwt", return_value=valid_access_token_payload)
        mocker.patch("api.api_v1.auth.auth.get_user_id", return_value=1)
        mocker.patch("api.api_v1.auth.auth.get_user_by_id", return_value=mock_user)

        result = await async_client.get(
            url="/api/v1/auth/me",
            headers={"Authorization": "Bearer access_token"},
        )
        assert result.status_code == status.HTTP_200_OK
        response = result.json()
        assert response.get("nickname") == "test_user"
        assert response.get("first_name") == "Test"
        assert response.get("last_name") == "User"
        assert response.get("email") == "user@example.com"
        assert response.get("is_active") is True
        assert response.get("is_superuser") is False

    @pytest.mark.asyncio
    async def test_me_failure_with_refresh_token(
        self,
        mocker,
        async_client: AsyncClient,
        valid_refresh_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.decode_jwt", return_value=valid_refresh_token_payload)

        result = await async_client.get(
            url="/api/v1/auth/me",
            headers={"Authorization": "Bearer access_token"},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json()["detail"] == "Invalid token type: 'refresh', expected 'access'"

    @pytest.mark.asyncio
    async def test_me_failure_with_wrong_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        result = await async_client.get(
            url="/api/v1/auth/me",
            headers={"Authorization": "Bearer wrong_token"},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json()["detail"] == "Invalid Token"
