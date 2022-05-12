from typing import Any

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
from src.app.music.consts import ImageSize


class AlbumService(ModelService):
    repository = repositories.AlbumRepository

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
    repository = repositories.TrackRepository

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
    repository = repositories.PlaylistRepository

    @classmethod
    async def get_pages(cls, offset: int, limit: int, url: URL, **kwargs) -> ItemList:
        playlists = await PlaylistService.all(**kwargs)
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
        async with database.connection() as conn:
            async with conn.transaction():
                playlist: models.Playlist = await super().create(schema, **kwargs)

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


class GenreService(ModelService):
    repository = repositories.GenreRepository


class ImageService(ModelService):
    repository = repositories.ImageRepository
