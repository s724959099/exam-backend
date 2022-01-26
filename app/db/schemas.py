"""
All schemas for FastAPI
"""
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Jwt auth setting
    """
    authjwt_secret_key: str = "secret"


class UserLogin(BaseModel):
    """
    For Login data
    """
    email: str = Field(..., description='Email')
    password: str = Field(..., description='Password')
