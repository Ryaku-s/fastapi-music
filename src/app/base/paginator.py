from typing import Sequence

from ormar import Model
from starlette.datastructures import URL


def paginate(
    items: Sequence[Model],
    offset: int,
    limit: int,
    url: URL
):
    total = len(items)

    next_page = _get_next_page(url, offset, limit, total)
    previous_page = _get_previous_page(url, offset, limit)

    return {
        'items': items[offset : offset + limit],
        'href': str(url),
        'next_page': next_page,
        'previous_page': previous_page,
        'offset': offset,
        'limit': limit,
        'total': total
    }


def _get_next_page(url: URL, offset: int, limit: int, total: int) -> str:
    return str(url.replace_query_params(
        offset=offset + limit,
        limit=limit
    )) if total > limit + offset else None


def _get_previous_page(url: URL, offset: int, limit: int) -> str:
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
