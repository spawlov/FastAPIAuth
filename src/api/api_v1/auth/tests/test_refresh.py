from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from core.models import User
from core.schemas.auth import TokenInfo


class TestRefresh:
    @pytest.mark.asyncio
    async def test_success_refresh(
        self,
        async_client: AsyncClient,
        mock_user: User,
        valid_refresh_token_payload: dict[str, Any],
        access_token: str,
    ) -> None:
        with patch(
            "api.api_v1.auth.auth.get_user_id",
            AsyncMock(return_value=1),
        ), patch(
            "api.api_v1.auth.auth.get_user_by_id",
            AsyncMock(return_value=mock_user),
        ), patch(
            "api.api_v1.auth.utils.decode_jwt",
            MagicMock(return_value=valid_refresh_token_payload),
        ), patch(
            "api.api_v1.auth.auth.get_access_token",
            AsyncMock(return_value=access_token),
        ):

            result = await async_client.post(
                "/api/v1/auth/refresh",
                headers={"Authorization": "Bearer refresh_token"},
            )
            assert result.status_code == status.HTTP_200_OK

            response = TokenInfo.model_validate(result.json())
            assert len(response.access_token.split(".")) == 3
            assert response.access_token == "jwt.access.token"  # noqa: S105
            assert response.token_type == "Bearer"  # noqa: S105

    @pytest.mark.asyncio
    async def test_failure_refresh_with_access_token(
        self,
        async_client: AsyncClient,
        valid_access_token_payload: dict[str, Any],
    ) -> None:
        with patch(
            "api.api_v1.auth.utils.decode_jwt",
            MagicMock(return_value=valid_access_token_payload),
        ):
            result = await async_client.post(
                "/api/v1/auth/refresh",
                headers={"Authorization": "Bearer assess_token"},
            )
            assert result.status_code == status.HTTP_401_UNAUTHORIZED
            assert result.json()["detail"] == "Invalid token type: 'access', expected 'refresh'"
