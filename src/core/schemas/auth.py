from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, SecretStr

TokenType = Literal[
    "access",
    "refresh",
]


class AuthUser(BaseModel):
    id: int  # noqa: A003, VNE003
    nickname: str
    password: str
    first_name: str | None
    last_name: str | None
    email: str
    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class SignInUser(BaseModel):
    username: str
    password: SecretStr

    model_config = ConfigDict(
        extra="forbid",
    )


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class BlacklistToken(BaseModel):
    jti: str
    user_id: int
    token_type: str
    reason: str
    ip_address: str
    user_agent: str
    created_at: datetime
    revoked_at: datetime

    model_config = ConfigDict(
        extra="forbid",
    )
