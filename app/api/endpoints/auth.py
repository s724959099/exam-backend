"""
Auth api
"""
from api.route_handler import init_router_with_log

router = init_router_with_log()


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


@router.post(
    '/login/',
    name='Login'
)
async def login():
    """TODO"""
    pass


@router.post(
    '/signup/',
    name='Signup'
)
async def signup():
    """TODO"""
    pass
