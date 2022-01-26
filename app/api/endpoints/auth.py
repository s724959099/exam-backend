"""
Auth api
"""
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
        deleted=False,
    )
    if not user or not user.check_password(user_login.password):
        raise HTTPException(status_code=401, detail='Bad email or password')

    access_token = authorize.create_access_token(subject=user_login.email)
    refresh_token = authorize.create_refresh_token(subject=user_login.email)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.post('/refresh/', name='Refresh Token')
def refresh(authorize: AuthJWT = Depends()):
    """
    Refresh token by headers
    """
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)
    refresh_token = authorize.create_refresh_token(subject=current_user)
    return {'access_token': new_access_token, 'refresh_token': refresh_token}


@router.get(
    '/demo/',
    name='Refresh Token'
)
async def demo(
        authorize: AuthJWT = Depends(),
):
    """TODO"""
    authorize.jwt_required()

    current_user = authorize.get_jwt_subject()
    return {'user': current_user}


@router.post(
    '/signup/',
    name='Signup'
)
async def signup():
    """TODO"""
    pass
