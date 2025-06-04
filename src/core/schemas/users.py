from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    id: int  # noqa: A003, VNE003
    nickname: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserCreate(BaseModel):
    nickname: str
    email: EmailStr
    password: str
