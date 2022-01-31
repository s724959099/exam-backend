"""UserLogin schemas"""

import re

from db import models
from pydantic import BaseModel, Field, validator
from db.schemas.utils import validate


class UserSignup(BaseModel):
    """
    User signup schema
    """
    email: str = Field(..., description='Email')
    password: str = Field(..., description='Password')
    name: str = Field(..., description='name')

    # noinspection PyMethodParameters
    @validator('password')
    def password_validate(cls, v):  # pylint: disable=E0213 It is pydantic syntax
        """Validate passowrd"""
        return validate.password_validate(v)

    # noinspection PyMethodParameters
    @validator('email')
    def email_validate(cls, v):  # pylint: disable=E0213 It is pydantic syntax
        """Email formtat validate and user register"""
        pattern = re.compile(
            r'^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+'
            r'((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$'
        )
        if not pattern.match(v):
            raise ValueError('Please input email format')

        user = models.User.get(email=v)
        if user:
            raise ValueError('Email is register')
        return v
