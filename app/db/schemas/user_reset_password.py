"""UserResetPassword schemas"""

from pydantic import BaseModel, Field


class UserResetPassword(BaseModel):
    """
    For reset password
    """
    old_password: str = Field(..., description='Old password')
    new_password: str = Field(..., description='New password')
