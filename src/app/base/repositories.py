from typing import Type, TypeVar

from ormar import Model
from pydantic import BaseModel


CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)


class ModelRepository:
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
    async def create(cls, **kwargs) -> Model:
        return await cls.model.objects.create(**kwargs)

    @classmethod
    async def update(cls, obj: Model, **kwargs) -> Model:
        return await obj.update(**kwargs)

    @classmethod
    async def delete(cls, **kwargs) -> None:
        await cls.model.objects.filter(**kwargs).delete()

    @classmethod
    async def exists(cls, *args, **kwargs) -> bool:
        return await cls.model.objects.filter(*args, **kwargs).exists()

    @classmethod
    async def get_or_create(cls, **kwargs):
        return await cls.model.objects.get_or_create(**kwargs)
