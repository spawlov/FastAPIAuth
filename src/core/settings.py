import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent


class AuthJWT(BaseModel):
    token_url: str = "/api/v1/auth/login"
    algorithm: str = "RS256"
    private_key: str = Path(BASE_DIR / "certs/jwt-private.pem").read_text()
    public_key: str = Path(BASE_DIR / "certs/jwt-public.pem").read_text()
    exp_minutes: int = 15


class APIV1Settings(BaseModel):
    prefix: str = "/v1"


class APISettings(BaseModel):
    prefix: str = "/api"
    v1: APIV1Settings = APIV1Settings()


class DBSettings(BaseModel):
    url: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class RunSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class AppSettings(BaseSettings):
    api: APISettings = APISettings()
    auth_jwt: AuthJWT = AuthJWT()
    db: DBSettings
    run: RunSettings = RunSettings()

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=(".env", ".env.dev", ".env.prod", ".env.test"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="APP__",
        extra="ignore",
    )


settings = AppSettings()
