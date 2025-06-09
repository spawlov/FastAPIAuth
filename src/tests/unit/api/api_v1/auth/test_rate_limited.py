import pytest
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.api_v1.auth.utils import RATE_LIMIT_DATA, rate_limited


@pytest.mark.asyncio
async def test_rate_limited() -> None:
    RATE_LIMIT_DATA.clear()

    @rate_limited(max_calls=5, time_frame=1)
    async def mock_login(
        request: Request,
        session: AsyncSession | None,
        form_data: OAuth2PasswordRequestForm,
    ):
        return {"message": "OK"}

    request = Request(
        scope={
            "type": "http",
            "client": ("127.0.0.1", 8080),
        },
    )
    form_data = OAuth2PasswordRequestForm(  # noqa: S106
        username="user",
        password="password",
        grant_type="password",
    )
    for _ in range(5):
        result = await mock_login(
            request,
            None,
            form_data,
        )
        assert result == {"message": "OK"}


@pytest.mark.asyncio
async def test_rate_limited_block() -> None:
    RATE_LIMIT_DATA.clear()

    @rate_limited(max_calls=1, time_frame=1)
    async def mock_login(
        request: Request,
        session: AsyncSession | None,
        form_data: OAuth2PasswordRequestForm,
    ):
        return {"message": "OK"}

    request = Request(
        scope={
            "type": "http",
            "client": ("127.0.0.1", 8080),
        },
    )
    form_data = OAuth2PasswordRequestForm(  # noqa: S106
        username="user",
        password="password",
        grant_type="password",
    )
    await mock_login(request, None, form_data)

    with pytest.raises(HTTPException) as exc:
        await mock_login(request, None, form_data)

    assert exc.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert exc.value.detail == "Too many requests. Try again later."
