from typing import Any

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth.utils import create_jwt
from core.schemas.auth import TokenType


class TestCreateJWT:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("token_type", ["access", "refresh"])
    async def test_create_jwt(
        self,
        token_type: TokenType,
        mocker: MockerFixture,
        session: AsyncSession,
        valid_access_token_payload: dict[str, Any],
    ) -> None:
        mocker.patch("api.api_v1.auth.utils.create_jwt_record", return_value=None)
        result: str = await create_jwt(
            session=session,
            token_type=token_type,
            token_payload=valid_access_token_payload,
            expires=5,
        )
        assert isinstance(result, str)
        assert len(result.split(".")) == 3
