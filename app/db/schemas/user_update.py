"""UserUpdate schemas"""

from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    """
    For user update
    only update user name
    """
    name: str = Field(..., description='name')
