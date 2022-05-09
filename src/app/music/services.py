from typing import Any, Type

from ormar import Model

from src.core.db import database
from src.app.music import models
from src.app.music.consts import ImageSize
from src.utils.audio import upload_audio
from src.utils.image import upload_image
from src.app.base.services import CreateSchema, ModelService, UpdateSchema
from src.app.base.uploads import (
    get_album_image_upload_path,
    get_track_upload_path,
    get_playlist_image_upload_path
)


class GenreService(ModelService):
    model: Type[Model] = models.Genre


class AlbumService(ModelService):
    model: Type[Model] = models.Album

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

    @classmethod
    async def create(
        cls,
        schema: CreateSchema | None = None,
        **kwargs
    ) -> Model:
        upload_path = get_album_image_upload_path()
        small_image_path = upload_image(upload_path, schema.image, (100, 100))
        normal_image_path = upload_image(upload_path, schema.image, (450, 450))

        genre = await GenreService.get_object_or_404(id=schema.genre)

        async with database.connection() as conn:
            async with conn.transaction():
                album: models.Album = await super().create(
                    **schema.dict(exclude={'image', 'genre'}),
                    **kwargs,
                    duration_ms=0,
                    genre=genre
                )
                small_image_obj = await ImageService.create(
                    url=small_image_path,
                    size=ImageSize.SMALL
                )
                normal_image_obj = await ImageService.create(
                    url=normal_image_path,
                    size=ImageSize.NORMAL
                )
                await album.images.add(small_image_obj)
                await album.images.add(normal_image_obj)

        return album

    @classmethod
    async def update(cls, schema: UpdateSchema, **kwargs) -> Model:
        album = await super().update(schema, **kwargs)

        if schema.image:
            upload_path = get_album_image_upload_path()
            small_image_path = upload_image(upload_path, schema.image, (100, 100))
            normal_image_path = upload_image(upload_path, schema.image, (450, 450))
            for image in album.images:
                if image.size == ImageSize.NORMAL:
                    url = normal_image_path
                else:
                    url = small_image_path
                await image.update(url=url)

        return album

    @classmethod
    async def _pre_save(cls, schema: CreateSchema | UpdateSchema) -> dict[str, Any]:
        return schema.dict(exclude={'image'}, exclude_none=True)


class ImageService(ModelService):
    model: Type[Model] = models.Image


class TrackService(ModelService):
    model: Type[Model] = models.Track

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

    @classmethod
    async def _pre_save(
        cls,
        schema: CreateSchema | UpdateSchema
    ) -> dict[str, Any]:
        to_save = schema.dict(exclude={'file'}, exclude_none=True)

        upload_path = get_track_upload_path()
        if schema.file:
            file_path, duration_ms = await upload_audio(upload_path, schema.file)
            to_save.update({
                'file': file_path,
                'duration_ms': duration_ms
            })

        return to_save


class PlaylistService(ModelService):
    model = models.Playlist

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls.model.objects.select_related([
            'author',
            'artists',
            'tracks',
            'tracks__artist',
            'images'
        ]).get_or_none(**kwargs)

    @classmethod
    async def create(cls, schema: CreateSchema | None = None, **kwargs) -> Model:
        async with database.connection() as conn:
            async with conn.transaction():
                playlist: models.Playlist = await super().create(schema, **kwargs)

                upload_path = get_playlist_image_upload_path()
                small_image_path = upload_image(upload_path, schema.image, (100, 100))
                normal_image_path = upload_image(upload_path, schema.image, (450, 450))

                small_image_obj = await ImageService.create(
                    url=small_image_path,
                    size=ImageSize.SMALL
                )
                normal_image_obj = await ImageService.create(
                    url=normal_image_path,
                    size=ImageSize.NORMAL
                )
                await playlist.images.add(small_image_obj)
                await playlist.images.add(normal_image_obj)

        return playlist

    @classmethod
    async def update(cls, schema: UpdateSchema, **kwargs) -> Model:
        playlist = await super().update(schema, **kwargs)

        if schema.image:
            upload_path = get_playlist_image_upload_path()
            small_image_path = upload_image(upload_path, schema.image, (100, 100))
            normal_image_path = upload_image(upload_path, schema.image, (450, 450))
            for image in playlist.images:
                if image.size == ImageSize.NORMAL:
                    url = normal_image_path
                else:
                    url = small_image_path
                await image.update(url=url)

        return playlist

    @classmethod
    async def _pre_save(cls, schema: CreateSchema | UpdateSchema) -> dict[str, Any]:
        return schema.dict(exclude={'image'}, exclude_none=True)


class SavedTrackService(ModelService):
    model = models.SavedTrack

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        saved_tracks = await cls.model.objects.select_related([
            'track',
            'track__album',
            'track__artist',
            'track__album__genre',
            'track__album__artist',
            'track__album__images'
        ]).all(**kwargs)
        return [saved_track.track.dict() for saved_track in saved_tracks]


class SavedAlbumService(ModelService):
    model = models.SavedAlbum

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        saved_albums = await cls.model.objects.select_related([
            'album',
            'album__artist',
            'album__genre',
            'album__images',
            'album__tracks',
            'album__tracks__artist'
        ]).all(**kwargs)
        return [saved_album.album.dict() for saved_album in saved_albums]
