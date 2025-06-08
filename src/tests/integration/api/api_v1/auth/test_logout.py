from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient


class TestLogout:
    @pytest.mark.asyncio
    async def test_successful_logout(
        self,
        mocker,
        async_client: AsyncClient,
        valid_access_token_payload,
        access_token: str,
    ) -> None:
        mocker.patch("api.api_v1.auth.auth.get_user_id", return_value=1)
        mocker.patch("api.api_v1.auth.auth.revoke_token", return_value=None)
        mocker.patch("api.api_v1.auth.utils.decode_jwt", return_value=valid_access_token_payload)

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
        mocker,
        async_client: AsyncClient,
        valid_access_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.auth.get_user_id", return_value=1)
        mocker.patch("api.api_v1.auth.auth.revoke_all_user_tokens", return_value=None)
        mocker.patch("api.api_v1.auth.utils.decode_jwt", return_value=valid_access_token_payload)

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
