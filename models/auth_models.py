"""Authentication models"""
from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    username: str


class AuthCredentials(BaseModel):
    username: str
    password: str
    created_at: datetime

