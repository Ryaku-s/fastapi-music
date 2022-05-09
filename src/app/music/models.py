from datetime import datetime

import ormar
from sqlalchemy import func

from src.core.db import BaseMeta
from src.app.user.models import User
from src.app.music.consts import AlbumType, ImageSize


class Genre(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=100)


class Image(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    url: str = ormar.String(max_length=255)
    size: str = ormar.String(max_length=6, choices=list(ImageSize))


class Album(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=100)
    artist: User = ormar.ForeignKey(User, skip_reverse=True, nullable=False)
    genre: Genre = ormar.ForeignKey(Genre, skip_reverse=True, nullable=False)
    album_type: str = ormar.String(max_length=6, choices=list(AlbumType))
    release_date: datetime = ormar.Date(server_default=func.now())
    images: list[Image] = ormar.ManyToMany(Image, skip_reverse=True)
    duration_ms: int = ormar.Integer(minimum=0)


class Track(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=100)
    artist: User = ormar.ForeignKey(User, skip_reverse=True, nullable=False)
    album: Album = ormar.ForeignKey(Album, nullable=False)
    file: str = ormar.String(max_length=255)
    is_playable: bool = ormar.Boolean(default=True, nullable=False)
    explicit: bool = ormar.Boolean(nullable=False)
    text: str | None = ormar.Text(nullable=True)
    duration_ms: int = ormar.Integer(minimum=0)
    number: int = ormar.Integer(minimum=1, default=1)


class Playlist(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=100)
    author: User = ormar.ForeignKey(User, skip_reverse=True, nullable=False)
    artists: list[User] = ormar.ManyToMany(
        User,
        related_name='in_playlists',
        skip_reverse=True
    )
    tracks: list[Track] = ormar.ManyToMany(Track, skip_reverse=True)
    images: list[Image] = ormar.ManyToMany(Image, skip_reverse=True)
    duration_ms: int = ormar.Integer(minimum=0)


class SavedAlbum(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'saved_albums'
        constraints = [ormar.UniqueColumns('user', 'album')]

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(User, skip_reverse=True, nullable=False)
    album: Album = ormar.ForeignKey(Album, skip_reverse=True, nullable=False)


class SavedTrack(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'saved_tracks'
        constraints = [ormar.UniqueColumns('user', 'track')]

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(User, skip_reverse=True, nullable=False)
    track: Track = ormar.ForeignKey(Track, skip_reverse=True, nullable=False)


class SavedPlaylist(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'saved_playlists'
        constraints = [ormar.UniqueColumns('user', 'playlist')]

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(User, skip_reverse=True, nullable=False)
    playlist: Playlist = ormar.ForeignKey(
        Playlist,
        skip_reverse=True,
        nullable=False
    )
