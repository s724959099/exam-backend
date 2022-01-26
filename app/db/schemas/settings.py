"""Settings schemas"""
from pydantic import BaseModel


class Settings(BaseModel):
    """
    Jwt auth setting
    """
    authjwt_secret_key: str = "secret"
