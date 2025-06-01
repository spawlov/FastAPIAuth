from pydantic import BaseModel, EmailStr, SecretStr, ConfigDict


class UserRead(BaseModel):
    id: int
    nickname: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserCreate(BaseModel):
    nickname: str
    email: EmailStr
    password: str
