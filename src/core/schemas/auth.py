from typing import Literal, TypeVar

from pydantic import BaseModel, ConfigDict, SecretStr


class AuthUser(BaseModel):
    id: int
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
    token_type: str
