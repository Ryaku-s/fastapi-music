from ormar import Model

from src.app.base.repositories import ModelRepository
from src.app.music import models


class AlbumRepository(ModelRepository):
    model = models.Album

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls.model.objects.select_related([
            'artist',
            'images',
            'genre',
            'tracks__artist'
        ]).all(**kwargs)

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls.model.objects.select_related([
            'artist',
            'images',
            'genre',
            'tracks__artist'
        ]).get_or_none(**kwargs)


class TrackRepository(ModelRepository):
    model = models.Track

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls.model.objects.select_related([
            'artist',
            'album',
            'album__artist',
            'album__genre',
            'album__images'
        ]).all(**kwargs)

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls.model.objects.select_related([
            'artist',
            'album',
            'album__artist',
            'album__genre',
            'album__images'
        ]).get_or_none(**kwargs)


class PlaylistRepository(ModelRepository):
    model = models.Playlist

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls.model.objects.select_related([
            'author',
            'artists',
            'tracks',
            'tracks__artist',
            'images'
        ]).all(**kwargs)

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls.model.objects.select_related([
            'author',
            'artists',
            'tracks',
            'tracks__artist',
            'images'
        ]).get_or_none(**kwargs)


class GenreRepository(ModelRepository):
    model = models.Genre


class ImageRepository(ModelRepository):
    model = models.Image
