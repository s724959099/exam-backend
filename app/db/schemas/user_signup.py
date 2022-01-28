"""UserLogin schemas"""

import re

from db import models
from pydantic import BaseModel, Field, validator


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
        """
        Password validate
        - contains at least one lower character
        - contains at least one upper character
        - contains at least one digit character
        - contains at least one special character
        - contains at least 8 characters
        """
        if not re.findall(r'[a-z]', v):
            raise ValueError('Contains at least one lower character')
        elif not re.findall(r'[A-Z]', v):
            raise ValueError('Contains at least one upper character')
        elif not re.findall(r'[0-9]', v):
            raise ValueError('Contains at least one digit character')
        elif not re.findall(r'[^\w\s]', v):
            raise ValueError('Contains at least one special character')
        elif not re.findall(r'.{8,}', v):
            raise ValueError('Contains at least 8 characters')

        return v

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
