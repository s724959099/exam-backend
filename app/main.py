"""
Fastapi server main program
"""
import os

import uvicorn
from api.router import api_router
from config import DEBUG, config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.middleware.sessions import SessionMiddleware
from utils.log import setup_logging

version = os.environ.get('TAG', '0.0.1')
app = FastAPI(title='AVL-Exam', version=version)
app.debug = DEBUG
origins = [
    '*',
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


@app.get('/version/')
def get_version():
    """
    get version tag
    """
    return {
        'version': version,
        'DEMO1': config.get('DEMO1', default=None),
        'DEMO2': config.get('DEMO2', default=None),
    }


# noinspection PyUnresolvedReferences,PyUnusedLocal
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(
        request: Request,  # pylint:disable=W0613 request is necessary for exception_handler
        exc: AuthJWTException
):
    """
    Catch all AuthJWTException
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.message}
    )


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
