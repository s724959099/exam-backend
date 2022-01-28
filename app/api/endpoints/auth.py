"""
Auth api
"""
import datetime

from api.deps import update_user_from_jwt
from api.route_handler import init_router_with_log
from db import models, schemas
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from pony.orm import db_session

router = init_router_with_log()


@AuthJWT.load_config
def get_config():
    """
    JWT load config
    Returns:
         Settings
    """
    return schemas.Settings()


@router.get('/login/google/', name='Google Auth login')
async def google_login():
    """TODO"""
    pass


@router.get(
    '/login/google/authorized/',
    name='Google Oauth authorized redirect'
)
async def google_login_authorized():
    """TODO"""
    pass


@router.get('/login/facebook/', name='Facebook Auth login')
async def facebook_login():
    """TODO"""
    pass


@router.get(
    '/login/facebook/authorized/',
    name='Facebook Oauth authorized redirect'
)
async def facebook_login_authorized():
    """TODO"""
    pass


@db_session
@router.post(
    '/login/',
    name='Login'
)
async def login(
        user_login: schemas.UserLogin,
        authorize: AuthJWT = Depends(),
):
    """
    Only for web login
    Returns:
        { access_token:<TOKEN>, refresh_token: <TOKEN>}
    Raises:
        HttpExcetpion(401) for fail
    """
    user = models.User.get(
        email=user_login.email,
        register_from=1,
        verify=True,
        deleted=False,
    )
    if not user or not user.check_password(user_login.password):
        raise HTTPException(status_code=401, detail='Bad email or password')

    access_token = authorize.create_access_token(subject=user_login.email)
    refresh_token = authorize.create_refresh_token(subject=user_login.email)

    # Set the JWT cookies in the response
    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)
    return {'msg': 'Successfully login'}


@router.post('/refresh/', name='Refresh Token')
async def refresh(authorize: AuthJWT = Depends()):
    """
    Refresh token by headers
    """
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    access_token = authorize.create_access_token(subject=current_user)
    refresh_token = authorize.create_refresh_token(subject=current_user)
    user = models.User.get(email=current_user, deleted=False)
    # update user last_login_time
    if user:
        with db_session:
            user.last_login_time = datetime.datetime.now()

    # Set the JWT cookies in the response
    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)
    return {'msg': 'The token has been refresh'}


@router.delete('/logout/')
async def logout(authorize: AuthJWT = Depends()):
    """
    Because the JWT are stored in an httponly cookie now, we cannot
    log the user out by simply deleting the cookies in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    update_user_from_jwt(authorize)
    authorize.unset_jwt_cookies()
    return {'msg': 'Successfully logout'}
