from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr

Username = Annotated[str, Field(
    min_length=3, max_length=50, pattern=r"^[a-z][a-z0-9._-]*$"  # Regex: definiert erlaubte usernamen
)]
Password = Annotated[SecretStr, Field(min_length=4, max_length=128)]


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: Username
    password: Password


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: Literal["reader", "staff"]


class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
