from typing import Any, Type, TypeVar

from ormar import Model
from fastapi import HTTPException
from pydantic import BaseModel
from starlette.datastructures import URL

from src.app.base.schemas import ItemList
from src.app.base.paginator import paginate
from src.app.base.repositories import ModelRepository

CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)


class ModelService:
    repository: Type[ModelRepository]

    @classmethod
    async def get(cls, **kwargs) -> Model:
        return await cls.repository.get(**kwargs)

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls.repository.all(**kwargs)

    @classmethod
    async def get_pages(
        cls,
        offset: int,
        limit: int,
        url: URL,
        **kwargs
    ) -> ItemList:
        items = await cls.repository.all(**kwargs)
        return paginate(items, offset, limit, url)

    @classmethod
    async def get_object_or_none(cls, **kwargs):
        return await cls.repository.get_object_or_none(**kwargs)

    @classmethod
    async def get_object_or_404(cls, **kwargs) -> Model:
        obj = await cls.repository.get_object_or_none(**kwargs)

        if not obj:
            raise HTTPException(
                status_code=404,
                detail='{} does not exist'.format(
                    cls.repository.model.get_name(lower=False)
                )
            )
        return obj

    @classmethod
    async def create(
        cls,
        schema: CreateSchema | None = None,
        **kwargs
    ) -> Model:
        if schema:
            schema_dict = await cls._pre_save(schema)
            kwargs.update(**schema_dict)
        return await cls.repository.create(**kwargs)

    @classmethod
    async def update(cls, schema: UpdateSchema, **kwargs) -> Model:
        obj: Model = await cls.get_object_or_404(**kwargs)

        schema_dict = await cls._pre_save(schema)
        return await cls.repository.update(
            obj,
            **schema_dict
        )

    @classmethod
    async def exists(cls, *args, **kwargs):
        return await cls.repository.exists(*args, **kwargs)

    @classmethod
    async def _pre_save(
        cls,
        schema: CreateSchema | UpdateSchema
    ) -> dict[str, Any]:
        return schema.dict(exclude_none=True)
