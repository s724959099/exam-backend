"""
Usr api
"""
import datetime
import uuid

from api.route_handler import init_router_with_log
from api.deps import update_user_from_jwt
from config import config
from db import models, schemas
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pony.orm import db_session
from utils import encrypt, mail

router = init_router_with_log()


@db_session
@router.get(
    '/profile/',
    name='Self User profile',
    response_model=schemas.UserResponse
)
async def profile(
        authorize: AuthJWT = Depends(),
):
    """
    Get self user profile
    Raises:
        raise 404 for Not found
    """
    user = update_user_from_jwt(authorize)
    if not user:
        raise HTTPException(status_code=404, detail='Not found user')
    return user


@db_session
@router.post(
    '/reset-password/',
    name='Reset password'
)
async def reset_password(
        user_reset_password: schemas.UserResetPassword,
        authorize: AuthJWT = Depends(),
):
    """
    User reset password
    Raises:
        422 -> password is not correct
    """
    user = update_user_from_jwt(authorize, use_db_session=False)
    if not user.check_password(user_reset_password.old_password):
        raise HTTPException(status_code=422, detail='password is not correct')
    salt = encrypt.get_salt()
    hash_password = encrypt.get_hash(user_reset_password.new_password, salt)
    user.salt = encrypt.transfter_salt_to_str(salt)
    user.password = hash_password
    user.updated_at = datetime.datetime.now()
    return {'msg': 'success'}


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
    verify_url = f'{config.get("FRONTEND_BASE_URL")}/user/verify/{verify_id}'
    with db_session:
        models.User(
            email=usersignup.email,
            name=usersignup.name,
            register_from=1,
            password=hash_password,
            salt=encrypt.transfter_salt_to_str(salt),
            verify=False,
            verify_id=verify_id
        )
    mail.send_email(
        to=usersignup.email,
        subject='Verify your account',
        message=f'link: {verify_url}'
    )
    return {
        'msg': 'Please go to receive email to verify account'
    }


@router.get(
    '/verify/{verify_id}/',
    name='Verify user by verify id'
)
async def verify(
        verify_id: str,
        authorize: AuthJWT = Depends(),
):
    """Verify by id"""
    user = models.User.get(verify_id=verify_id, deleted=False)
    if not user:
        return JSONResponse(status_code=404, content=dict(msg='not found'))
    with db_session:
        user.updated_at = datetime.datetime.now()
        user.verify = True
        user.verify_id = None
        user.last_login_time = datetime.datetime.now()
    access_token = authorize.create_access_token(subject=user.email)
    refresh_token = authorize.create_refresh_token(subject=user.email)

    # Set the JWT cookies in the response
    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)
    return {'msg': 'Successfully verify'}
