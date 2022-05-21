from typing import Any
from fastapi import HTTPException

from ormar import Model
from starlette.datastructures import URL
from src.app.base.schemas import ItemList

from src.core.db import database
from src.utils.audio import upload_audio
from src.utils.image import upload_image
from src.app.base.paginator import paginate
from src.app.base.services import CreateSchema, ModelService, UpdateSchema
from src.app.base.uploads import (
    get_album_image_upload_path,
    get_track_upload_path,
    get_playlist_image_upload_path
)
from src.app.music import models, repositories
from src.app.music.consts import AlbumType, ImageSize


class AlbumService(ModelService):
    _repository = repositories.AlbumRepository

    @classmethod
    async def is_available_to_upload(cls, album: models.Album) -> None:
        if album.album_type == AlbumType.SINGLE and await TrackService\
            .get_object_or_none(album=album):
            raise HTTPException(
                status_code=403,
                detail='A single album can only have one track'
            )

    @classmethod
    async def get_pages(cls, offset: int, limit: int, url: URL, **kwargs):
        albums = await cls.all(**kwargs)
        for i, album in enumerate(albums):
            albums[i] = {
                **album.dict(exclude={'tracks'}),
                'tracks': paginate(
                    album.tracks,
                    0,
                    15,
                    URL('http://127.0.0.1:8000/api/v1/albums/{}/tracks?offset=0&limit=15'\
                        .format(album.id))
                )
            }
        return paginate(albums, offset, limit, url)

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

        await album.genre.load()
        await album.artist.load()
        return {
            **album.dict(exclude={'tracks'}),
            'tracks': {
                'items': [],
                'href': 'http://127.0.0.1:8000/api/v1/albums/{}/tracks?offset=0&limit=15'\
                    .format(album.id),
                'next_page': None,
                'previous_page': None,
                'total': 0,
                'offset': 0,
                'limit': 15
            }
        }

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

    @classmethod
    async def _pre_save(cls, schema: CreateSchema | UpdateSchema) -> dict[str, Any]:
        return schema.dict(exclude={'image'}, exclude_none=True)


class TrackService(ModelService):
    _repository = repositories.TrackRepository

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
    _repository = repositories.PlaylistRepository

    @classmethod
    async def get_pages(cls, offset: int, limit: int, url: URL, **kwargs) -> ItemList:
        playlists = await cls._repository.all(**kwargs)
        for i, playlist in enumerate(playlists):
            playlists[i] = {
                **playlist.dict(exclude={'tracks', 'artists'}),
                'artists': playlist.artists[:15],
                'tracks': paginate(
                    playlist.tracks,
                    0,
                    15,
                    URL('http://127.0.0.1:8000/api/v1/playlists/{}/tracks'
                            '?offset=0&limit=15'.format(playlist.id))
                )
            }
        return paginate(playlists, offset, limit, url)

    @classmethod
    async def create(cls, schema: CreateSchema | None = None, **kwargs) -> Model:
        upload_path = get_playlist_image_upload_path()
        small_image_path = upload_image(
            upload_path,
            schema.image,
            (100, 100)
        )
        normal_image_path = upload_image(
            upload_path,
            schema.image,
            (450, 450)
        )

        async with database.connection() as conn:
            async with conn.transaction():
                playlist: models.Playlist = await super().create(schema, **kwargs)

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

        return {
            **playlist.dict(exclude={'tracks'}),
            'tracks': {
                'items': [],
                'href': 'http://127.0.0.1:8000/api/v1/albums/{}/tracks?offset=0&limit=15'\
                    .format(playlist.id),
                'next_page': None,
                'previous_page': None,
                'total': 0,
                'offset': 0,
                'limit': 15
            }
        }

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
    _repository = repositories.SavedTrackRepository


class SavedAlbumService(ModelService):
    _repository = repositories.SavedAlbumRepository


class SavedPlaylistService(ModelService):
    _repository = repositories.SavedPlaylistRepository


class GenreService(ModelService):
    _repository = repositories.GenreRepository


class ImageService(ModelService):
    _repository = repositories.ImageRepository
