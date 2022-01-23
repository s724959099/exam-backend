import typing
from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from utils.shopify import base_url as shopify_base_url
from utils import shopify
from utils.fetcher import fetch
from utils.fetcher import HttpxClient
from urllib.parse import urljoin
import json
from api.permission import get_user_by_token
from db import schemas
from log import logger
from api.route_handler import init_router_with_log
from db import models
from fastapi import BackgroundTasks

router = init_router_with_log()


def get_link_headers(r) -> dict:
    ret = dict()
    try:
        headers = dict(r.headers)
        if headers.get('Link'):
            ret['Link'] = headers.get('Link')
    except Exception:
        pass
    return ret


async def _graphql_api(query, variables, ip):
    url = shopify.storefront_api
    token = shopify.storefront_token
    headers = {
        'X-Shopify-Storefront-Access-Token': token,
        'X-Forwarded-For': ip,
        'REMOTE_ADDR': ip,
        'Client-IP': ip,
    }
    retries = 3
    async with HttpxClient(retries=retries) as client:
        r = await client.post(
            url, json=dict(query=query, variables=variables), headers=headers)
        if not r:
            return JSONResponse(content=dict(detail='requests error'), status_code=400)
        return JSONResponse(content=r.json(), status_code=r.status_code)


# noinspection PyUnusedLocal
@router.get("/config/")
async def get_config(
        user: schemas.User = Depends(get_user_by_token)
):
    res = models.ShopifySyncFlag.find_one()
    if res and '_id' in res:
        del res['_id']
    return res


@router.post("/graphql/getcheckout/")
async def getcheckout(
        request: Request,
        variables: typing.Union[
            typing.List[typing.Dict[str, typing.Any]],
            typing.Dict[str, typing.Any]
        ]
):
    query = """
    query GetCheckout($id: ID!) {
        node(id: $id) {
            ... on Checkout {
            id
            ready
            currencyCode
            subtotalPriceV2{
                amount
            }
            taxesIncluded
            totalTaxV2{
                amount
            }
            totalPriceV2 {
                amount
            }
            }
        }
    }
    """
    return await _graphql_api(query, variables, request.client.host)


@router.post("/graphql/createcheckout/")
async def createcheckout(
        request: Request,
        variables: typing.Union[
            typing.List[typing.Dict[str, typing.Any]],
            typing.Dict[str, typing.Any]
        ]
):
    query = """
    mutation checkoutCreate($lineItems: [CheckoutLineItemInput!]) {
        checkoutCreate(input: { lineItems: $lineItems }) {
          checkout {
            id
            webUrl
          }
          checkoutUserErrors {
            code
            field
            message
          }
        }
      }
    """
    return await _graphql_api(query, variables, request.client.host)


@router.post("/graphql/updatecheckoutemail/")
async def updatecheckoutemail(
        request: Request,
        variables: typing.Union[
            typing.List[typing.Dict[str, typing.Any]],
            typing.Dict[str, typing.Any]
        ]
):
    query = """
    mutation checkoutEmailUpdateV2($checkoutID: ID!, $email: String!) {
      checkoutEmailUpdateV2(checkoutId: $checkoutID, email: $email) {
        checkout {
          id
        }
        checkoutUserErrors {
          code
          field
          message
        }
      }
    }
    """
    return await _graphql_api(query, variables, request.client.host)


@router.post("/graphql/updatecheckoutattributes/")
async def updatecheckoutattributes(
        request: Request,
        variables: typing.Union[
            typing.List[typing.Dict[str, typing.Any]],
            typing.Dict[str, typing.Any]
        ]
):
    query = """
    mutation checkoutAttributesUpdateV2($checkoutID: ID!, $attributes: [AttributeInput!]) {
          checkoutAttributesUpdateV2(checkoutId: $checkoutID, input: { customAttributes: $attributes}) {
            checkout {
              id
            }
            checkoutUserErrors {
              code
              field
              message
            }
          }
        }
    """
    return await _graphql_api(query, variables, request.client.host)


@router.post("/graphql/updateshippingline/")
async def updateshippingline(
        request: Request,
        variables: typing.Union[
            typing.List[typing.Dict[str, typing.Any]],
            typing.Dict[str, typing.Any]
        ]
):
    query = """
    mutation checkoutShippingLineUpdate($checkoutID: ID!, $shippingRates: String!) {
          checkoutShippingLineUpdate(checkoutId: $checkoutID, shippingRateHandle: $shippingRates) {
            checkout {
              id
            }
            checkoutUserErrors {
              code
              field
              message
            }
          }
        }
    """
    return await _graphql_api(query, variables, request.client.host)


@router.post("/graphql/updatecheckoutshippingaddress/")
async def updatecheckoutshippingaddress(
        request: Request,
        variables: typing.Union[
            typing.List[typing.Dict[str, typing.Any]],
            typing.Dict[str, typing.Any]
        ]
):
    query = """
    mutation checkoutShippingAddressUpdateV2($checkoutID: ID!, $shippingAddress: MailingAddressInput!) {
          checkoutShippingAddressUpdateV2(checkoutId: $checkoutID, shippingAddress: $shippingAddress) {
            checkout {
              id
            }
            checkoutUserErrors {
              code
              field
              message
            }
          }
        }
    """
    return await _graphql_api(query, variables, request.client.host)


@router.post("/graphql/createcustomer/")
async def createcustomer(
        request: Request,
        variables: typing.Union[
            typing.List[typing.Dict[str, typing.Any]],
            typing.Dict[str, typing.Any]
        ]
):
    query = """
    mutation customerCreate($customerInfo: CustomerCreateInput!) {
          customerCreate(input: $customerInfo) {
            customer {
              id
            }
            customerUserErrors {
              code
              field
              message
            }
          }
        }
    """
    return await _graphql_api(query, variables, request.client.host)


@router.put("/order/{order_id:path}/note_attribute/")
async def put_note_attribute(
        order_id: str,
        note_attributes: typing.List[schemas.NoteAttribute]
):
    retries = 3
    url = f'{shopify_base_url}orders/{order_id}.json'
    data = []
    for el in note_attributes:
        data.append(el.dict())
    async with HttpxClient(retries=retries) as client:

        r = await client.put(url, json={
            'order': {'note_attributes': data}
        })
        if not r:
            return JSONResponse(content=dict(detail='requests error'), status_code=400)

        return JSONResponse(content=r.json(), status_code=r.status_code)


# noinspection PyUnusedLocal
@router.get("/{path:path}")
async def get(
        request: Request,
        user: schemas.User = Depends(get_user_by_token)
):
    shopify_url = urljoin(shopify_base_url, request.path_params.get('path'))
    if request.query_params:
        shopify_url += f'?{request.query_params}'
    async with fetch(shopify_url, type='get') as r:
        try:
            ret = await r.json()
            headers = get_link_headers(r)
            return JSONResponse(ret, status_code=r.status, headers=headers)
        except Exception:
            return JSONResponse(dict(detail=f'fetch error', suffix_url=request.path_params.get('path')),
                                status_code=500)


# noinspection PyUnusedLocal
@router.post("/{path:path}")
async def post(
        request: Request,
        user: schemas.User = Depends(get_user_by_token)
):
    try:
        body = await request.body()
        body = json.loads(body)
    except Exception:
        body = {}

    shopify_url = urljoin(shopify_base_url, request.path_params.get('path'))
    if request.query_params:
        shopify_url += f'?{request.query_params}'
    async with fetch(shopify_url, type='post', json=body, headers={}) as r:
        try:
            ret = await r.json()
            logger.info(f'post: {shopify_url} status: {r.status}')
            headers = get_link_headers(r)
            return JSONResponse(ret, status_code=r.status, headers=headers)
        except Exception:
            return JSONResponse(dict(detail=f'fetch error', suffix_url=request.path_params.get('path')),
                                status_code=500)


# noinspection PyUnusedLocal
@router.put("/{path:path}")
async def put(
        request: Request,
        user: schemas.User = Depends(get_user_by_token)
):
    try:
        body = await request.body()
        body = json.loads(body)
    except Exception:
        body = {}
    shopify_url = urljoin(shopify_base_url, request.path_params.get('path'))
    if request.query_params:
        shopify_url += f'?{request.query_params}'
    async with fetch(shopify_url, type='put', json=body) as r:
        try:
            ret = await r.json()
            headers = get_link_headers(r)
            return JSONResponse(ret, status_code=r.status, headers=headers)
        except Exception:
            return JSONResponse(dict(detail=f'fetch error', suffix_url=request.path_params.get('path')),
                                status_code=500)


# noinspection PyUnusedLocal
@router.delete("/{path:path}")
async def delete(
        request: Request,
        user: schemas.User = Depends(get_user_by_token)
):
    shopify_url = urljoin(shopify_base_url, request.path_params.get('path'))
    if request.query_params:
        shopify_url += f'?{request.query_params}'
    async with fetch(shopify_url, type='delete') as r:
        try:
            ret = await r.json()
            headers = get_link_headers(r)
            return JSONResponse(ret, status_code=r.status, headers=headers)
        except Exception:
            return JSONResponse(dict(detail=f'fetch error', suffix_url=request.path_params.get('path')),
                                status_code=500)


if __name__ == '__main__':
    print()
