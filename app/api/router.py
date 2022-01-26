"""
api_router all router with prefix api/
"""
from fastapi import APIRouter

from .endpoints import auth, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(user.router, prefix='/user', tags=['user'])
