from typing import Sequence
import fastapi

from ormar import Model
from fastapi import Request
from starlette.datastructures import URL


def paginate(
    items: Sequence[Model],
    offset: int,
    limit: int,
    request: Request
):
    total = len(items)

    next_page = _get_next(request.url, offset, limit, total)
    previous_page = _get_previous(request.url, offset, limit)

    return {
        'items': items[offset : offset + limit],
        'next_page': next_page,
        'previous_page': previous_page,
        'offset': offset,
        'limit': limit,
        'total': total
    }


def _get_next(url: URL, offset: int, limit: int, total: int) -> str:
    return str(url.replace_query_params(
        offset=offset + limit,
        limit=limit
    )) if total > limit + offset else None


def _get_previous(url: URL, offset: int, limit: int) -> str:
    if offset != 0:
        if offset >= limit:
            previous_page = str(url.replace_query_params(
                offset=offset - limit,
                limit=limit
            ))
        else:
            previous_page = str(url.replace_query_params(
                offset=0,
                limit=offset
            ))
    else:
        previous_page = None
    return previous_page
