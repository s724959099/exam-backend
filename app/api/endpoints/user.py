"""
Usr api
"""
import datetime
import uuid

from api.route_handler import init_router_with_log
from fastapi.responses import JSONResponse
from config import config
from db import models, schemas
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from pony.orm import db_session, flush
from utils import encrypt, mail

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
    verify_url = f'{config.get("FRONTEND_BASE_URL")}/user/verify/{verify_id}'
    models.User(
        email=usersignup.email,
        name=usersignup.name,
        register_from=1,
        password=hash_password,
        salt=encrypt.transfter_salt_to_str(salt),
        verify=False,
        verify_id=verify_id
    )
    flush()
    mail.send_email(
        to=usersignup.email,
        subject='Verify your account',
        message=f'link: {verify_url}'
    )
    return {
        'msg': 'Please go to receive email to verify account'
    }


@db_session
@router.get(
    '/verify/{verify_id}/',
    name='Verify user by verify id'
)
async def verify(
        verify_id: str,
        authorize: AuthJWT = Depends(),
):
    """Verify by id"""
    user = models.User.get(verify_id=verify_id)
    if not user:
        return JSONResponse(status_code=404, content=dict(msg='not found'))
    with db_session:
        user.updated_at = datetime.datetime.now()
        user.verify = True
        user.verify_id = None
    access_token = authorize.create_access_token(subject=user.email)
    refresh_token = authorize.create_refresh_token(subject=user.email)

    # Set the JWT cookies in the response
    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)
    return {"msg": "Successfully verify"}
