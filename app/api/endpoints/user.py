"""
Usr api
"""
import datetime
import uuid
from urllib.parse import urljoin

from api.deps import (Pagination, create_user_record, get_pagination_schema,
                      update_user_from_jwt)
from api.route_handler import init_router_with_log
from config import config
from db import models, schemas
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pony.orm import count, select
from utils import encrypt, mail

router = init_router_with_log()


@router.get(
    '/profile/',
    name='Self User profile',
    response_model=schemas.UserResponse
)
async def profile(
        authorize: AuthJWT = Depends(),
):
    """
    Get self user profile \n
    Raises: \n
        raise 404 -> Not found \n
    """
    user = update_user_from_jwt(authorize)
    if not user:
        raise HTTPException(status_code=404, detail='Not found user')
    return user


@router.get(
    '/',
    name='Get All users',
    response_model=get_pagination_schema(schemas.UserResponse),
)
async def get_users(
        page: Pagination = Depends(),
        authorize: AuthJWT = Depends(),
):
    """Get all users"""
    update_user_from_jwt(authorize)
    query = models.User.select()
    return await page.paginate(query)


@router.post(
    '/reset-password/',
    name='Reset password',
    response_model=schemas.MessageResponse
)
async def reset_password(
        user_reset_password: schemas.UserResetPassword,
        authorize: AuthJWT = Depends(),
):
    """
    User reset password \n
    Raises: \n
        422 -> password is not correct \n
    """
    user = update_user_from_jwt(authorize)
    if user.register_from != 1:
        raise HTTPException(
            status_code=422,
            detail='Signup is not using password'
        )
    if not user.check_password(user_reset_password.old_password):
        raise HTTPException(status_code=422, detail='Password is not correct')
    salt = encrypt.get_salt()
    hash_password = encrypt.get_hash(user_reset_password.new_password, salt)
    user.salt = encrypt.transfter_salt_to_str(salt)
    user.password = hash_password
    user.updated_at = datetime.datetime.now()
    return {'msg': 'success'}


@router.put(
    '/',
    name='update self user',
    response_model=schemas.MessageResponse
)
async def update_self_user(
        user_update: schemas.UserUpdate,
        authorize: AuthJWT = Depends(),
):
    """
    Uupdate suer user \n
    Raises: \n
        422 -> password is not correct \n
    """
    try:
        user = update_user_from_jwt(authorize)
    except Exception as e:
        from utils.log import logger
        logger.exception('oops')
        raise e

    user.name = user_update.name
    user.updated_at = datetime.datetime.now()
    return {'msg': 'success'}


@router.post(
    '/signup/',
    name='Signup',
    response_model=schemas.MessageResponse
)
async def signup(
        usersignup: schemas.UserSignup
):
    """User Signup"""
    salt = encrypt.get_salt()
    hash_password = encrypt.get_hash(usersignup.password, salt)
    verify_id = str(uuid.uuid4())
    verify_url = urljoin(
        config.get('FRONTEND_BASE_URL'),
        f'/user/verify/{verify_id}'
    )
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
    name='Verify user by verify id',
    response_model=schemas.MessageResponse
)
async def verify(
        verify_id: str,
        authorize: AuthJWT = Depends(),
):
    """Verify by id"""
    user = models.User.get(verify_id=verify_id, deleted=False)
    if not user:
        return JSONResponse(status_code=404, content=dict(msg='not found'))
    user.updated_at = datetime.datetime.now()
    user.verify = True
    user.verify_id = None
    # verify and to dashbaord
    user.login_count += 1
    create_user_record(user)
    access_token = authorize.create_access_token(subject=user.email)
    refresh_token = authorize.create_refresh_token(subject=user.email)

    # Set the JWT cookies in the response
    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)
    return {'msg': 'Successfully verify'}


# noinspection PyTypeChecker,PyChainedComparisons
@router.get(
    '/statistics/',
    name='Statistics',
    response_model=schemas.StatisticsResponse
)
async def statistics(
        authorize: AuthJWT = Depends(),
):
    """
    Statistics data
    """
    update_user_from_jwt(authorize)
    # get sign up count
    sign_up_count = models.User.select(lambda x: not x.deleted).count()

    # get today active sessions
    today = datetime.datetime.today()
    today_st = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_ed = today.replace(hour=23, minute=59, second=59, microsecond=59)
    today_active_count = models.User.select(
        lambda x:
        not x.deleted and
        today_ed >= x.last_login_time and
        x.last_login_time >= today_st
    ).count()

    # Average number of active session users in the last 7 days rolling.
    count_list = []
    for day in range(7):
        that_day = today - datetime.timedelta(days=day)
        day_st = that_day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_ed = that_day.replace(hour=23, minute=59, second=59,
                                  microsecond=59)
        total_count = select(
            count(record.user.id) for record in models.UserActivieRecord
            if record.created_at >= day_st and record.created_at <= day_ed
        ).first()
        count_list.append(total_count)

    last_7days_active_avg = round(sum(count_list) / 7, 2)

    return {
        'sign_up_count': sign_up_count,
        'today_active_count': today_active_count,
        'last_7days_active_avg': last_7days_active_avg,
    }
