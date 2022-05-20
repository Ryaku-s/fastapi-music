from enum import Enum


class ImageSize(str, Enum):
    SMALL = 'small'
    NORMAL = 'normal'


class AlbumType(str, Enum):
    ALBUM = 'album'
    SINGLE = 'single'
