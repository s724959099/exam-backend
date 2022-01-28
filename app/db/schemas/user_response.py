"""User Response schema"""
import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """
    User response schema
    """
    email: str = Field(..., description='email')
    name: str = Field(..., description='name')
    register_from: int = Field(..., description='register_from')
    verify: bool = Field(..., description='verify')
    login_count: int = Field(..., description='login_count')
    last_login_time: datetime.datetime = Field(
        None, description='last_login_time'
    )
    created_at: datetime.datetime = Field(..., description='created_at')

    class Config:
        """
        Orm model
        """
        orm_mode = True
