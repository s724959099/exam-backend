"""
Examples:
    router = init_router_with_log()
    @router.post('/login/')
    async def login():
        pass

"""
import typing

from fastapi import APIRouter, Request, Response
from fastapi.exceptions import HTTPException, ValidationError
from fastapi.routing import APIRoute
from utils.log import logger


class GzipRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, '_body'):
            body = await super().body()
            # noinspection PyAttributeOutsideInit
            self._body = body
        return self._body


class ErrorLoggingRoute(APIRoute):
    """Record all fail log"""

    def get_route_handler(self) -> typing.Callable:
        """Override old function"""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Log it if catch error"""
            try:
                request = GzipRequest(request.scope, request.receive)
                return await original_route_handler(request)
            except ValidationError as exc:
                body = await request.body()
                detail = {
                    'errors': exc.errors(),
                    'body': body.decode() if body is not None else None
                }
                query = {}
                for key in request.query_params:
                    query[key] = request.query_params[key]
                logger.error(
                    f'url:{request.url} status: {422} '
                    f'query: {query} '
                    f'detail: {detail} body: {body}'
                )
                raise HTTPException(status_code=422, detail=detail) from exc
            except HTTPException as exc:
                # 很多 api 都會來亂
                if exc.status_code == 401:
                    logger.info(
                        f'url:{request.url} status: {exc.status_code}')
                    raise exc
                body = await request.body()

                query = {}
                for key in request.query_params:
                    query[key] = request.query_params[key]
                logger.error(
                    f'url:{request.url} status: {exc.status_code} '
                    f'query: {query} '
                    f'detail: {exc.detail} body: {body}')
                raise exc

        return custom_route_handler


def init_router_with_log() -> APIRouter:
    """
    Initial router with ErrorLoggingRoute
    Returns:
        APIRouter with ErrorLoggingRoute
    """
    return APIRouter(route_class=ErrorLoggingRoute)
