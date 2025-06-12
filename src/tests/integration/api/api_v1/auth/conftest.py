from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from core.models import User
from main import main_app

from .mock_data import ACCESS_TOKEN, REFRESH_TOKEN, USER


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_user() -> User:
    return User(**USER)


@pytest.fixture
def access_token() -> str:
    return ACCESS_TOKEN


@pytest.fixture
def refresh_token() -> str:
    return REFRESH_TOKEN


@pytest.fixture
def valid_access_token_payload() -> dict[str, Any]:
    jwt_payload = {
        "type": "access",
        "sub": "1",
        "username": "test",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": "123-456-7890",
    }
    return jwt_payload


@pytest.fixture
def valid_refresh_token_payload() -> dict[str, Any]:
    jwt_payload = {
        "type": "refresh",
        "sub": "1",
        "username": "test",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
        "jti": "123-456-7890",
    }
    return jwt_payload
