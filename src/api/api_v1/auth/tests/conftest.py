import pytest
from httpx import ASGITransport, AsyncClient

from api.api_v1.auth.tests.mock_data import ACCESS_TOKEN, REFRESH_TOKEN, USER
from core.models import User
from main import main_app


@pytest.fixture
async def async_client() -> AsyncClient:
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
