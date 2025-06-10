import uuid
from datetime import timedelta
from typing import Any

import pytest
from jwt import InvalidKeyError, InvalidTokenError

from api.api_v1.auth.utils import decode_jwt, encode_jwt
from tests.unit.api.api_v1.auth.conftest import rsa_keys  # noqa: F401


class TestEncodeDecodeJWT:
    def test_encode_decode_jwt(
        self,
        valid_access_token_payload: dict[str, Any],
        rsa_keys: dict[str, str],  # noqa: F811
    ) -> None:
        jti = str(uuid.uuid4())
        access_token = encode_jwt(
            payload=valid_access_token_payload,
            expires_in=timedelta(minutes=5),
            jti=jti,
            private_key=rsa_keys["private_key"],
        )
        result = decode_jwt(
            access_token,
            public_key=rsa_keys["public_key"],
        )
        assert result["sub"] == valid_access_token_payload["sub"]
        assert result["username"] == valid_access_token_payload["username"]
        assert result["type"] == valid_access_token_payload["type"]
        assert result["jti"] == jti
        assert "iat" in result
        assert "exp" in result

    def test_failure_encode_jwt(
        self,
        valid_access_token_payload: dict[str, Any],
    ) -> None:
        with pytest.raises(InvalidKeyError):
            encode_jwt(
                payload=valid_access_token_payload,
                expires_in=timedelta(minutes=5),
                jti=str(uuid.uuid4()),
                private_key="wrong_private_key",
            )

    def test_failure_decode_jwt(
        self,
        rsa_keys: dict[str, str],  # noqa: F811
    ) -> None:
        with pytest.raises(InvalidTokenError):
            decode_jwt(  # noqa: S106
                token="Invalid_JWT",
                public_key=rsa_keys["public_key"],
            )
