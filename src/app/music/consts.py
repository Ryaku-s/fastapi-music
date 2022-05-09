from enum import Enum


class ImageSize(str, Enum):
    SMALL = 'small'
    NORMAL = 'normal'


class AlbumType(str, Enum):
    ALBUM = 'album'
    SINGLE = 'single'


# class AlbumVisibility(str, Enum):
#     ALL = 'all'
#     SUBS_ONLY = 'subs'
#     PRIVATE = 'private'
