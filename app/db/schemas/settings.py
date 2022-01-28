"""Settings schemas"""
from config import config
from pydantic import BaseModel


class Settings(BaseModel):
    """
    Jwt auth setting
    """
    authjwt_secret_key: str = config.get('session_secret_key')
    authjwt_token_location: set = {'cookies'}
    authjwt_cookie_secure: bool = False
    authjwt_cookie_csrf_protect: bool = True
    # add expire time for testing
    # authjwt_access_token_expires: int = 3
    # authjwt_refresh_token_expires: int = 10
