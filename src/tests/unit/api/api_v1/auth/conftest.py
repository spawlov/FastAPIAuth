from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest.fixture
def rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return {
        "private_key": private_pem.decode("utf-8"),
        "public_key": public_pem.decode("utf-8"),
    }


@pytest.fixture
def valid_access_token_payload() -> dict[str, Any]:
    jwt_payload = {
        "type": "access",
        "sub": "1",
        "username": "test",
    }
    return jwt_payload


@pytest.fixture
def valid_refresh_token_payload() -> dict[str, Any]:
    jwt_payload = {
        "type": "refresh",
        "sub": "1",
    }
    return jwt_payload
