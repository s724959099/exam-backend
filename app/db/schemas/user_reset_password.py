"""UserResetPassword schemas"""

from db.schemas.utils import validate
from pydantic import BaseModel, Field, validator


class UserResetPassword(BaseModel):
    """
    For reset password
    """
    old_password: str = Field(..., description='Old password')
    new_password: str = Field(..., description='New password')

    # noinspection PyMethodParameters
    @validator('old_password')
    def old_password_validate(cls, v):  # pylint: disable=E0213 It is pydantic syntax
        """Validate old passowrd"""
        return validate.password_validate(v)

    # noinspection PyMethodParameters
    @validator('new_password')
    def new_password_validate(cls, v):  # pylint: disable=E0213 It is pydantic syntax
        """Validate new passowrd"""
        return validate.password_validate(v)
