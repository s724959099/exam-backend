"""
API functions
"""
import datetime
import typing

from db import models
from fastapi_jwt_auth import AuthJWT
from pony.orm import db_session


def update_user(authorize: AuthJWT):
    """
    Update user by authorize.get_jwt_subject()
    get user then update user.last_login_time
    Args:
         authorize: AuthJWT
    Returns:
        User or None
    """
    authorize.jwt_required()
    email = authorize.get_jwt_subject()
    user = models.User.get(email=email, deleted=False)
    if user:
        with db_session:
            user.last_login_time = datetime.datetime.now()
