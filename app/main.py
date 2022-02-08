"""
Fastapi server main program
"""
import inspect
import os
import re

import uvicorn
from api.router import api_router
from config import DEBUG, config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi_jwt_auth.exceptions import AuthJWTException
from pony.orm import db_session
from starlette.middleware.sessions import SessionMiddleware
from utils.log import setup_logging

FAST_API_TITLE = 'AVL-Exam'
VERSION = os.environ.get('TAG', '0.0.1')
app = FastAPI(title=FAST_API_TITLE, version=VERSION)


def custom_openapi():
    """Swagger UI page has authorize"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=FAST_API_TITLE,
        version=VERSION,
        routes=app.routes,
    )
    openapi_schema['info']['x-logo'] = {
        'url': 'https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png'
    }

    cookie_security_schemes = {
        'AuthJWTCookieAccess': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-CSRF-TOKEN'
        },
        'AuthJWTCookieRefresh': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-CSRF-TOKEN'
        }
    }
    refresh_token_cookie = {
        'name': 'refresh_token_cookie',
        'in': 'cookie',
        'required': False,
        'schema': {
            'title': 'refresh_token_cookie',
            'type': 'string'
        }
    }
    access_token_cookie = {
        'name': 'access_token_cookie',
        'in': 'cookie',
        'required': False,
        'schema': {
            'title': 'access_token_cookie',
            'type': 'string'
        }
    }

    if 'components' in openapi_schema:
        openapi_schema['components'].update(
            {'securitySchemes': cookie_security_schemes}
        )
    else:
        openapi_schema['components'] = {
            'securitySchemes': cookie_security_schemes
        }

    api_router_ = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router_:
        path = getattr(route, 'path')
        endpoint = getattr(route, 'endpoint')
        methods = [method.lower() for method in getattr(route, 'methods')]

        for method in methods:
            # access_token
            if (
                    re.search('jwt_required', inspect.getsource(endpoint)) or
                    re.search(
                        'update_user_from_jwt',
                        inspect.getsource(endpoint)
                    ) or
                    re.search(
                        'fresh_jwt_required',
                        inspect.getsource(endpoint)
                    ) or
                    re.search('jwt_optional', inspect.getsource(endpoint))
            ):
                try:
                    openapi_schema['paths'][path][method]['parameters'].append(
                        access_token_cookie
                    )
                except KeyError:
                    openapi_schema['paths'][path][method].update(
                        {'parameters': [access_token_cookie]}
                    )

                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != 'get':
                    openapi_schema['paths'][path][method].update({
                        'security': [{'AuthJWTCookieAccess': []}]
                    })

            # refresh_token
            if re.search(
                    'jwt_refresh_token_required',
                    inspect.getsource(endpoint)
            ):
                try:
                    openapi_schema['paths'][path][method]['parameters'].append(
                        refresh_token_cookie
                    )
                except KeyError:
                    openapi_schema['paths'][path][method].update(
                        {'parameters': [refresh_token_cookie]}
                    )

                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != 'get':
                    openapi_schema['paths'][path][method].update({
                        'security': [{'AuthJWTCookieRefresh': []}]
                    })

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.debug = DEBUG
origins = [
    'http://localhost:3000',
    'https://avl-exam.tk',
    'https://avl-exam.tk/',
]
secret_key = config.get('session_secret_key')
app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router, prefix='/api')


@app.get('/api/version/')
def get_version():
    """
    get version tag
    """
    return {
        'version': VERSION,
    }


# noinspection PyUnresolvedReferences,PyUnusedLocal
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(
        request: Request,  # pylint:disable=W0613 request is necessary for exception_handler
        exc: AuthJWTException
):
    """
    Catch all AuthJWTException
    custom all 422 auth exception is 403
    (signature fail code is same with valueerror in pydantic)
    """
    status_code = exc.status_code
    if status_code == 422:
        status_code = 403
    return JSONResponse(
        status_code=status_code,
        content={'detail': exc.message}
    )


@app.middleware('http')
async def add_pony(request: Request, call_next):
    """Add db session with each api"""
    with db_session:
        response = await call_next(request)
        return response


@app.on_event('startup')
async def startup():
    """
    intitial log before start server
    """
    setup_logging()


if __name__ == '__main__':
    if DEBUG:
        uvicorn.run(
            'main:app',
            host='0.0.0.0',
            port=5000,
            log_level='info',
            reload=True,
            workers=1,
            debug=True,
        )
