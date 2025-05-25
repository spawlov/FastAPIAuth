from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class AppSettings(BaseSettings):
    db: DBSettings
    api: APISettings = APISettings()

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=(".env", ".env.dev", ".env.prod", ".env.test"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="APP__",
        extra="ignore",
    )


settings = AppSettings()
