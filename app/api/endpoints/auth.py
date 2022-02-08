"""
Auth api
"""
from urllib.parse import urljoin

from api.deps import create_user_record, update_user_from_jwt
from api.route_handler import init_router_with_log
from authlib.integrations.starlette_client import OAuth
from config import config
from db import models, schemas
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from starlette.config import Config

router = init_router_with_log()

config_data = {
    'GOOGLE_CLIENT_ID': config.get('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': config.get('GOOGLE_CLIENT_SECRET'),
    'FACEBOOK_CLIENT_ID': config.get('FACEBOOK_CLIENT_ID'),
    'FACEBOOK_CLIENT_SECRET': config.get('FACEBOOK_CLIENT_SECRET'),
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
google_url = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=google_url,
    client_kwargs={'scope': 'openid email profile'},
)
oauth.register(
    name='facebook',
    api_base_url='https://graph.facebook.com/v7.0/',
    access_token_url='https://graph.facebook.com/v7.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v7.0/dialog/oauth',
    client_kwargs={'scope': 'email public_profile'},
)


@AuthJWT.load_config
def get_config():
    """
    JWT load config
    Returns:
         Settings
    """
    return schemas.Settings()


@router.get('/login/google/', name='Google Auth login')
async def google_login(request: Request):
    """Login with google auth"""
    redirect_uri = urljoin(
        config.get('BACKEND_BASE_URL'),
        '/api/auth/login/google/authorized/'
    )
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get(
    '/login/google/authorized/',
    name='Google Oauth authorized redirect'
)
async def google_login_authorized(
        request: Request,
        authorize: AuthJWT = Depends()
):
    """
    Get google authorized \n
    Signup user if email is not found \n
    Create new acctess_token in cookie then redirect to frontent
    """
    # get user from token
    token = await oauth.google.authorize_access_token(request)
    user_data = await oauth.google.parse_id_token(request, token)
    # get user or signup a user
    user = models.User.get(email=user_data['email'])
    if not user:
        user = models.User(
            email=user_data['email'],
            name=user_data['name'],
            register_from=3,  # google
            verify=True,
        )
    else:
        user.login_count += 1
    create_user_record(user)

    access_token = authorize.create_access_token(subject=user_data['email'])
    refresh_token = authorize.create_refresh_token(subject=user_data['email'])

    # Set the JWT cookies in the response
    frontend_uri = urljoin(config.get('FRONTEND_BASE_URL'), '/dashboard')
    response = RedirectResponse(frontend_uri)
    authorize.set_access_cookies(access_token, response)
    authorize.set_refresh_cookies(refresh_token, response)
    return response


@router.get('/login/facebook/', name='Facebook Auth login')
async def facebook_login(request: Request):
    """Login with facebook auth"""
    redirect_uri = urljoin(
        config.get('BACKEND_BASE_URL'),
        '/api/auth/login/facebook/authorized/'
    )
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get(
    '/login/facebook/authorized/',
    name='Facebook Oauth authorized redirect'
)
async def facebook_login_authorized(
        request: Request,
        authorize: AuthJWT = Depends()
):
    """
    Get facebook authorized \n
    Signup user if email is not found \n
    Create new acctess_token in cookie then redirect to frontent
    """
    # get user from token
    token = await oauth.facebook.authorize_access_token(request)
    res = await oauth.facebook.get('me?fields=name,email,picture', token=token)
    user_data = res.json()

    # # get user or signup a user
    user = models.User.get(email=user_data['email'])
    if not user:
        user = models.User(
            email=user_data['email'],
            name=user_data['name'],
            register_from=2,  # facebook
            verify=True,
        )
    else:
        user.login_count += 1

    create_user_record(user)
    access_token = authorize.create_access_token(subject=user_data['email'])
    refresh_token = authorize.create_refresh_token(subject=user_data['email'])

    # Set the JWT cookies in the response
    frontend_uri = urljoin(config.get('FRONTEND_BASE_URL'), '/dashboard')
    response = RedirectResponse(frontend_uri)
    authorize.set_access_cookies(access_token, response)
    authorize.set_refresh_cookies(refresh_token, response)
    return response


@router.post(
    '/login/',
    name='Login'
)
async def login(
        user_login: schemas.UserLogin,
        authorize: AuthJWT = Depends(),
):
    """
    Only for web login \n
    Returns: \n
        { access_token:<TOKEN>, refresh_token: <TOKEN>} \n
    Raises: \n
        HttpExcetpion(401) for fail \n
    """
    user = models.User.get(
        email=user_login.email,
        register_from=1,
        verify=True,
        deleted=False,
    )

    if not user or not user.check_password(user_login.password):
        raise HTTPException(status_code=401, detail='Bad email or password')

    user.login_count += 1
    create_user_record(user)
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
    if not user:
        raise HTTPException(status_code=404, detail='No found user')
    create_user_record(user)

    # Set the JWT cookies in the response
    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)
    return {'msg': 'The token has been refresh'}


@router.delete('/logout/')
async def logout(authorize: AuthJWT = Depends()):
    """
    Because the JWT are stored in an httponly cookie now, we cannot \n
    log the user out by simply deleting the cookies in the frontend. \n
    We need the backend to send us a response to delete the cookies.
    """
    update_user_from_jwt(authorize)
    authorize.unset_jwt_cookies()
    return {'msg': 'Successfully logout'}
