from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from starlette import status


class TestLogout:
    @pytest.mark.asyncio
    async def test_successful_logout(
        self,
        async_client: AsyncClient,
        valid_access_token_payload,
        access_token: str,
    ) -> None:
        with patch(
            "api.api_v1.auth.auth.get_user_id",
            AsyncMock(return_value=1),
        ), patch(
            "api.api_v1.auth.auth.revoke_token",
            AsyncMock(return_value=None),
        ), patch(
            "api.api_v1.auth.utils.decode_jwt",
            MagicMock(return_value=valid_access_token_payload),
        ):
            result = await async_client.post(
                url="/api/v1/auth/logout",
                headers={"Authorization": "Bearer access_token"},
                params={"logout_all": "false"},
            )
            assert result.status_code == status.HTTP_200_OK
            assert result.json()["message"] == "success"
            assert result.json()["details"] == "Logged out successfully"

    @pytest.mark.asyncio
    async def test_successful_logout_all(
        self,
        async_client: AsyncClient,
        valid_access_token_payload,
    ) -> None:
        with patch(
            "api.api_v1.auth.auth.get_user_id",
            AsyncMock(return_value=1),
        ), patch(
            "api.api_v1.auth.auth.revoke_all_user_tokens",
            AsyncMock(return_value=None),
        ), patch(
            "api.api_v1.auth.utils.decode_jwt",
            MagicMock(return_value=valid_access_token_payload),
        ):
            result = await async_client.post(
                url="/api/v1/auth/logout",
                headers={"Authorization": "Bearer access_token"},
                params={"logout_all": "true"},
            )
            assert result.status_code == status.HTTP_200_OK
            assert result.json()["message"] == "success"
            assert result.json()["details"] == "All sessions terminated successfully"

    @pytest.mark.asyncio
    async def test_failure_logout(
        self,
        async_client: AsyncClient,
    ) -> None:
        result = await async_client.post(
            url="/api/v1/auth/logout",
            headers={
                "Authorization": "Bearer wrong_token",
            },
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json()["detail"] == "Invalid Token"
