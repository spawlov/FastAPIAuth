from typing import Any
from unittest.mock import patch

import pytest
from fastapi import HTTPException, status

from api.api_v1.auth.utils import get_current_token_payload


def test_get_current_token_payload_valid(
    valid_access_token_payload: dict[str, Any],
) -> None:
    with patch("api.api_v1.auth.utils.decode_jwt", return_value=valid_access_token_payload):
        result = get_current_token_payload(token="Valid_JWT")  # noqa: S106
        assert result == valid_access_token_payload


def test_get_current_token_payload_invalid() -> None:
    with pytest.raises(HTTPException) as exc:
        get_current_token_payload(token="Invalid_JWT")  # noqa: S106
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid Token"
