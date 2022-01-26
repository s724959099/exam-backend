"""Settings schemas"""
from pydantic import BaseModel


class Settings(BaseModel):
    """
    Jwt auth setting
    """
    authjwt_secret_key: str = "secret"
    # add expire time for testing
    # authjwt_access_token_expires: int = 3
    # authjwt_refresh_token_expires: int = 10
