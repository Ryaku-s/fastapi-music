from datetime import datetime
from fastapi import Body, File, UploadFile
from pydantic import BaseModel
from src.app.base.forms import model_form_factory

from src.app.music import models
from src.app.base.schemas import ItemList, get_pydantic


Genre = get_pydantic(models.Genre, 'Genre', exclude={'id', 'albums'})

AlbumFromModel = get_pydantic(models.Album, 'Album', exclude={
    'id',
    'release_date',
    'duration_ms',
    'tracks',
    'artist',
    'genre',
    'images'
})

TrackFromModel = get_pydantic(
    models.Track,
    'Track',
    exclude={'id', 'album', 'duration_ms', 'file', 'artist'}
)
ImageRelated = get_pydantic(
    models.Image,
    'ImageRelated',
    exclude={'id', 'album'}
)


class Artist(BaseModel):
    id: int
    username: str
    avatar: str | None
    about: str | None
    date_joined: datetime
    is_active: bool


class AlbumCreate(AlbumFromModel):
    genre: int = Body(..., gt=0, description='ID of genre')
    image: UploadFile = File(...)


class AlbumUpdate(BaseModel):
    title: str | None = Body(None, max_length=100)
    album_type: str | None = Body(None)
    genre: int | None = Body(None, gt=0, description='ID of genre')
    image: UploadFile | None = File(None)


class TrackCreate(TrackFromModel):
    file: UploadFile = File(...)


class TrackUpdate(BaseModel):
    title: str | None = Body(None, max_length=100)
    is_playable: bool | None = Body(None)
    explicit: bool | None = Body(None)
    text: str | None
    number: int | None = Body(1, ge=1)
    file: UploadFile | None = File(None)


class PlaylistCreate(BaseModel):
    title: str = Body(...)
    image: UploadFile = File(...)


class PlaylistUpdate(BaseModel):
    title: str | None = Body(None)
    image: UploadFile | None = File(None)


class AlbumRelated(
    models.Album.get_pydantic(exclude={'artist', 'tracks', 'genre', 'images'})
):
    genre: Genre
    artist: Artist
    images: list[ImageRelated]


class TrackRelated(models.Track.get_pydantic(exclude={'artist', 'album'})):
    artist: Artist


class AlbumOut(
    models.Album.get_pydantic(exclude={'artist', 'genre', 'images'})
):
    genre: Genre
    artist: Artist
    tracks: list[TrackRelated]
    images: list[ImageRelated]


class TrackOut(TrackRelated):
    album: AlbumRelated


class PlaylistOut(
    models.Playlist.get_pydantic(exclude={'author', 'artists', 'tracks', 'images'})
):
    author: Artist
    artists: list[Artist]
    tracks: list[TrackRelated]
    images: list[ImageRelated]


class AlbumList(ItemList):
    items: list[AlbumOut]


class TrackList(ItemList):
    items: list[TrackOut]


class PlaylistAddTrack(BaseModel):
    tracks: list[int] = Body(..., description='IDs of tracks')


class TrackSave(BaseModel):
    id: int = Body(..., description='ID of track')


class AlbumSave(BaseModel):
    id: int = Body(..., description='ID of album')


AlbumCreateForm = model_form_factory(AlbumCreate)
AlbumUpdateForm = model_form_factory(AlbumUpdate)
TrackCreateForm = model_form_factory(TrackCreate)
TrackUpdateForm = model_form_factory(TrackUpdate)
PlaylistCreateForm = model_form_factory(PlaylistCreate)
PlaylistUpdateForm = model_form_factory(PlaylistUpdate)
