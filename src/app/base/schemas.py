from typing import Type

from ormar import Model
from pydantic import BaseModel


def get_pydantic(
    model: Type[Model],
    name: str | None = None,
    include: set | dict | None = None,
    exclude: set | dict | None = None
) -> Type[BaseModel]:
    pydantic = model.get_pydantic(include=include, exclude=exclude)
    if name:
        pydantic.__name__ = name
    return pydantic


class Message(BaseModel):
    msg: str


class ExceptionMessage(BaseModel):
    detail: str


class ItemList(BaseModel):
    items: list
    href: str
    next_page: str | None = None
    previous_page: str | None = None
    total: int
    offset: int
    limit: int
