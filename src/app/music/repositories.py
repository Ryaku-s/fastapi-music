from ormar import Model

from src.app.base.repositories import ModelRepository
from src.app.music import models


class AlbumRepository(ModelRepository):
    _model = models.Album

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls._model.objects.select_related([
            'artist',
            'images',
            'genre',
            'tracks__artist'
        ]).all(**kwargs)

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls._model.objects.select_related([
            'artist',
            'images',
            'genre',
            'tracks__artist'
        ]).get_or_none(**kwargs)


class TrackRepository(ModelRepository):
    _model = models.Track

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls._model.objects.select_related([
            'artist',
            'album',
            'album__artist',
            'album__genre',
            'album__images'
        ]).all(**kwargs)

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls._model.objects.select_related([
            'artist',
            'album',
            'album__artist',
            'album__genre',
            'album__images'
        ]).get_or_none(**kwargs)


class PlaylistRepository(ModelRepository):
    _model = models.Playlist

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        return await cls._model.objects.select_related([
            'author',
            'artists',
            'tracks',
            'tracks__artist',
            'tracks__album',
            'tracks__album__artist',
            'tracks__album__genre',
            'images'
        ]).all(**kwargs)

    @classmethod
    async def get_object_or_none(cls, **kwargs) -> Model:
        return await cls._model.objects.select_related([
            'author',
            'artists',
            'tracks',
            'tracks__artist',
            'tracks__album__artist',
            'tracks__album__genre',
            'images'
        ]).get_or_none(**kwargs)


class GenreRepository(ModelRepository):
    _model = models.Genre


class ImageRepository(ModelRepository):
    _model = models.Image


class SavedTrackRepository(ModelRepository):
    _model = models.SavedTrack

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        saved_tracks = await cls._model.objects.select_related([
            'track',
            'track__album',
            'track__artist',
            'track__album__genre',
            'track__album__artist',
            'track__album__images'
        ]).all(**kwargs)
        return [saved_track.track.dict() for saved_track in saved_tracks]


class SavedAlbumRepository(ModelRepository):
    _model = models.SavedAlbum

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        saved_albums = await cls._model.objects.select_related([
            'album',
            'album__artist',
            'album__genre',
            'album__images',
            'album__tracks',
            'album__tracks__artist'
        ]).all(**kwargs)
        return [saved_album.album.dict() for saved_album in saved_albums]


class SavedPlaylistRepository(ModelRepository):
    _model = models.SavedPlaylist

    @classmethod
    async def all(cls, **kwargs) -> list[Model]:
        saved_playlists = await cls._model.objects.select_related([
            'playlist',
            'playlist__author',
            'playlist__artists',
            'playlist__tracks',
            'playlist__tracks__artist',
            'playlist__images'
        ]).all(**kwargs)
        return [saved_playlist.dict() for saved_playlist in saved_playlists]
