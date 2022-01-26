"""
Usr api
"""
from api.route_handler import init_router_with_log
from db import models, schemas
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from pony.orm import db_session

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
        deleted=False,
    )
    if not user:
        raise HTTPException(status_code=404, detail='Not found user')
    return {
        'name': user.name,
        'email': user.email,
        'created_at': user.created_at
    }
