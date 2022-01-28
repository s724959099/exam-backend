"""
API functions
"""
import datetime
import typing

from db import models
from fastapi_jwt_auth import AuthJWT
from pony.orm import db_session


def update_user_from_jwt(authorize: AuthJWT, use_db_session: bool = True):
    """
    Update user by authorize.get_jwt_subject()
    get user then update user.last_login_time
    Args:
         authorize: AuthJWT
         use_db_session: flag with use db_session
    Returns:
        User or None
    Notes:
        Each api can only use db_session once
    Raises:
        Status code 422 from authorize.jwt_required()
    """
    authorize.jwt_required()
    email = authorize.get_jwt_subject()
    user = models.User.get(email=email, deleted=False)
    if user:
        if use_db_session:
            with db_session:
                user.last_login_time = datetime.datetime.now()
        else:
            user.last_login_time = datetime.datetime.now()

    return user
