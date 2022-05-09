from typing import Type

from ormar import Model
from fastapi import HTTPException
from src.app.music.models import Album, Playlist, Track

from src.app.user.models import User


def _is_user_obj_author(
    user: User,
    obj: Type[Model],
    author_field: str = 'author'
) -> None:
    if getattr(obj, author_field).id != user.id:
        raise HTTPException(
            status_code=403,
            detail='Current user doesn\'t have enough privileges'
        )


def is_user_album_author(
    user: User,
    album: Album
) -> None:
    return _is_user_obj_author(user, album, 'artist')


def is_user_track_author(
    user: User,
    track: Track
) -> None:
    return _is_user_obj_author(user, track, 'artist')


def is_user_playlist_author(
    user: User,
    playlist: Playlist
) -> None:
    return _is_user_obj_author(user, playlist)
