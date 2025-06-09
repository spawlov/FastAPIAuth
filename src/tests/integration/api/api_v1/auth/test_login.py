import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient

from api.api_v1.auth.utils import RATE_LIMIT_DATA
from core.models import User
from core.schemas.auth import TokenInfo


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(
        self,
        mocker,
        async_client: AsyncClient,
        mock_user: User,
        access_token: str,
        refresh_token: str,
    ):
        RATE_LIMIT_DATA.clear()
        mocker.patch("api.api_v1.auth.auth.get_auth_user", return_value=mock_user)
        mocker.patch("api.api_v1.auth.auth.get_access_token", return_value=access_token)
        mocker.patch("api.api_v1.auth.auth.get_refresh_token", return_value=refresh_token)

        form_data = {
            "username": "test_user",
            "password": "user_pass",
        }
        result = await async_client.post(
            url="/api/v1/auth/login",
            data=form_data,
        )
        assert result.status_code == status.HTTP_200_OK

        response = TokenInfo.model_validate(result.json())
        assert len(response.access_token.split(".")) == 3
        assert len(response.refresh_token.split(".")) == 3
        assert response.token_type == "Bearer"  # noqa: S105

    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials(
        self,
        mocker,
        async_client: AsyncClient,
    ):
        RATE_LIMIT_DATA.clear()
        mocker.patch(
            "api.api_v1.auth.auth.get_auth_user",
            side_effect=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            ),
        )

        form_data = {
            "username": "wrong_user",
            "password": "wrong_pass",
        }
        result = await async_client.post(
            url="/api/v1/auth/login",
            data=form_data,
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json()["detail"] == "Invalid username or password"

    @pytest.mark.asyncio
    async def test_login_with_rate_limited(
        self,
        mocker,
        async_client: AsyncClient,
        mock_user: User,
        access_token: str,
        refresh_token: str,
    ):
        RATE_LIMIT_DATA.clear()
        mocker.patch("api.api_v1.auth.auth.get_auth_user", return_value=mock_user)
        mocker.patch("api.api_v1.auth.auth.get_access_token", return_value=access_token)
        mocker.patch("api.api_v1.auth.auth.get_refresh_token", return_value=refresh_token)

        form_data = {
            "username": "test_user",
            "password": "user_pass",
        }
        for _ in range(5):
            result = await async_client.post(
                url="/api/v1/auth/login",
                data=form_data,
            )
            assert result.status_code == status.HTTP_200_OK
        result = await async_client.post(
            url="/api/v1/auth/login",
            data=form_data,
        )
        assert result.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert result.json()["detail"] == "Too many requests. Try again later."
