"""UserLogin schemas"""

from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    """
    For Login data
    """
    email: str = Field(..., description='Email')
    password: str = Field(..., description='Password')
