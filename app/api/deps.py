"""
API functions
"""
import datetime
import typing
from typing import List, Optional

from db import models
from fastapi import Query, Request
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel, Field


def create_user_record(user: models.User):
    """Update login time and create new user active record"""
    user.last_login_time = datetime.datetime.now()
    models.UserActivieRecord(
        user=user
    )


def update_user_from_jwt(authorize: AuthJWT):
    """
    Update user by authorize.get_jwt_subject()
    get user then update user.last_login_time
    Args:
         authorize: AuthJWT
    Returns:
        User or None
    Notes:
        Each api can only use db_session once
    Raises:
        Status code 422 from authorize.jwt_required()
    """
    authorize.jwt_required()
    email = authorize.get_jwt_subject()
    user = models.User.get(email=email, deleted=False)
    if user:
        create_user_record(user)

    return user


class Pagination:
    """
    from fastapi conrtib to get it
    i fix some code which only can fit to mongo
    ----
    Query params parser and db collection paginator in one.
    Use it as dependency in route, then invoke `paginate` with serializer:
    .. code-block:: python
        app = FastAPI()
        class SomeSerializer(ModelSerializer):
            class Meta:
                model = SomeModel
        @app.get("/")
        async def list(pagination: Pagination = Depends()):
            filter_kwargs = {}
            return await pagination.paginate(
                serializer_class=SomeSerializer, **filter_kwargs
            )
    Subclass this pagination to define custom
    default & maximum values for offset & limit:
    .. code-block:: python
        class CustomPagination(Pagination):
            default_offset = 90
            default_limit = 1
            max_offset = 100`
            max_limit = 2000
    :param request: starlette Request object
    :param offset: query param of how many records to skip
    :param limit: query param of how many records to show
    """

    default_offset = 0
    default_limit = 10
    max_offset = None
    max_limit = 100

    def __init__(
            self,
            request: Request,
            offset: int = Query(default=default_offset, ge=0, le=max_offset),
            limit: int = Query(default=default_limit, ge=1, le=max_limit),
    ):
        self.request = request
        self.offset = offset
        self.limit = limit
        self.model = None
        self.count = None
        self.list = []

    async def get_count(self, **kwargs) -> int:
        """
        Retrieves counts for query list, filtered by kwargs.
        :param kwargs: filters that are proxied in db query
        :return: number of found records
        """
        self.count = await self.model.count(**kwargs)
        return self.count

    def get_next_url(self) -> typing.Optional[str]:
        """
        Constructs `next` parameter in resulting JSON,
        produces URL for next "page" of paginated results.
        :return: URL for next "page" of paginated results.
        """
        if self.offset + self.limit >= self.count:
            return None
        return str(
            self.request.url.include_query_params(
                limit=self.limit, offset=self.offset + self.limit
            )
        )

    def get_previous_url(self) -> typing.Optional[str]:
        """
        Constructs `previous` parameter in resulting JSON,
        produces URL for previous "page" of paginated results.
        :return: URL for previous "page" of paginated results.
        """
        if self.offset <= 0:
            return None

        if self.offset - self.limit <= 0:
            return str(self.request.url.remove_query_params(keys=['offset']))

        return str(
            self.request.url.include_query_params(
                limit=self.limit, offset=self.offset - self.limit
            )
        )

    async def paginate(
            self,
            query: Query
    ) -> dict:
        """
        Actual pagination function, takes serializer class,
        filter options as kwargs and returns dict with the following fields:
            * count - counts for query list, filtered by kwargs
            * next - URL for next "page" of paginated results
            * previous - URL for previous "page" of paginated results
            * result - actual list of records (dicts)
        :param query:
        :return: dict that should be returned as a response
        """
        self.count = query.count()
        return {
            'count': self.count,
            'next': self.get_next_url(),
            'previous': self.get_previous_url(),
            'data': query.limit(self.limit, offset=self.offset)[:],
        }


def get_pagination_schema(schema) -> typing.Union[type, BaseModel]:
    """Generate Pagination schema
    Returns:
        PageModel
    """

    class PageModel(BaseModel):
        """Response Schema for Pagination"""
        count: int = Field(..., description='total count')
        next: Optional[str] = Field(None, description='next page')
        previous: Optional[str] = Field(None, description='previous page')
        data: List[schema] = Field(
            ..., description=f'{schema.__name__} list'
        )

    class_ = type(f'{schema.__name__}Page', (PageModel,), {})

    return class_
