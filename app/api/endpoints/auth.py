"""
Auth api
"""
from api.route_handler import init_router_with_log

router = init_router_with_log()


@router.get('/login/google/', name='Google Auth login')
async def google_login():
    pass


@router.get('/login/google/authorized/', name='Google Oauth authorized redirect')
async def google_login_authorized():
    pass
