from datetime import datetime
import os


def _make_directories(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_avatar_upload_path() -> str:
    path = 'media/img/avatars/{}/'.format(
        str(int(datetime.utcnow().strftime('%d%m%Y')))
    )
    _make_directories(path)
    return path


def get_album_image_upload_path() -> str:
    path = 'media/img/albums/{}/'.format(
        str(int(datetime.utcnow().strftime('%d%m%Y')))
    )
    _make_directories(path)
    return path


def get_track_upload_path() -> str:
    path = 'media/audio/tracks/{}/'.format(
        str(int(datetime.utcnow().strftime('%d%m%Y')))
    )
    _make_directories(path)
    return path


def get_playlist_image_upload_path() -> str:
    path = 'media/img/playlists/{}/'.format(
        str(int(datetime.utcnow().strftime('%d%m%Y')))
    )
    _make_directories(path)
    return path 
