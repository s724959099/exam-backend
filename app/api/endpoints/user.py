"""
Usr api
"""
import uuid

from api.route_handler import init_router_with_log
from db import models, schemas
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from pony.orm import db_session
from utils import encrypt

router = init_router_with_log()


@db_session
@router.get(
    '/profile/',
    name='Self User profile'
)
async def profile(
        authorize: AuthJWT = Depends(),
):
    """
    Get self user profile
    Raises:
        raise 404 for Not found
    """
    authorize.jwt_required()
    email = authorize.get_jwt_subject()
    user = models.User.get(
        email=email,
        verify=True,
        deleted=False,
    )
    if not user:
        raise HTTPException(status_code=404, detail='Not found user')
    return {
        'name': user.name,
        'email': user.email,
        'created_at': user.created_at
    }


@db_session
@router.post(
    '/signup/',
    name='Signup'
)
async def signup(
        usersignup: schemas.UserSignup
):
    """User Signup"""
    salt = encrypt.get_salt()
    hash_password = encrypt.get_hash(usersignup.password, salt)
    verify_id = str(uuid.uuid4())
    models.User(
        email=usersignup.email,
        name=usersignup.name,
        register_from=1,
        password=hash_password,
        salt=encrypt.transfter_salt_to_str(salt),
        verify=False,
        verify_id=verify_id
    )
    return {
        'msg': 'Please go to receive email to verify account'
    }


@router.get(
    '/verify/{verify_id}/',
    name='Verify user by verify id'
)
async def verify(
        verify_id: str
):
    """Verify by id"""
    return {
        'msg': 'Please go to receive email to verify account'
    }
