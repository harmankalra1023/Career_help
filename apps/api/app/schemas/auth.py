from typing import Optional
from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str
    country: Optional[str] = "global"
    locale: Optional[str] = "en"


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    country: str
    locale: str
