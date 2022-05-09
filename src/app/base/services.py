from typing import Any, Sequence, Type, TypeVar

from ormar import Model
from fastapi import HTTPException, Request
from pydantic import BaseModel


CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)


class ModelService:
    model: Type[Model] = None

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls.model.objects.all(**kwargs)

    @classmethod
    async def get(cls, **kwargs) -> Model:
        return await cls.model.objects.get(**kwargs)

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls.model.objects.get_or_none(**kwargs)

    @classmethod
    async def get_object_or_404(cls, **kwargs) -> Model:
        obj = await cls.get_object_or_none(**kwargs)

        if not obj:
            raise HTTPException(
                status_code=404,
                detail='{} does not exist'.format(
                    cls.model.get_name(lower=False)
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
            kwargs.update(schema_dict)
        return await cls.model.objects.create(**kwargs)

    @classmethod
    async def update(cls, schema: UpdateSchema, **kwargs) -> Model:
        obj: Model = await cls.get_object_or_404(**kwargs)
        schema_dict = await cls._pre_save(schema)
        return await obj.update(**schema_dict)

    @classmethod
    async def delete(cls, **kwargs) -> None:
        await cls.model.objects.filter(**kwargs).delete()

    @classmethod
    async def exists(cls, **kwargs) -> bool:
        return await cls.model.objects.filter(**kwargs).exists()

    @classmethod
    async def get_or_create(cls, **kwargs):
        return await cls.model.objects.get_or_create(**kwargs)

    @classmethod
    async def _pre_save(
        cls,
        schema: CreateSchema | UpdateSchema
    ) -> dict[str, Any]:
        return schema.dict(exclude_none=True)
