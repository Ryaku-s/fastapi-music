import os
import string
from typing import IO
from random import sample
from PIL import Image, ImageOps
from tempfile import SpooledTemporaryFile

from fastapi import HTTPException, UploadFile

from src.config import settings


def upload_image(
    upload_path: str,
    file: UploadFile,
    size = tuple[int, int]
) -> str:
    filename, extension = file.filename.split('.')

    if extension not in settings.ALLOWED_IMAGE_FORMAT_EXTENSIONS:
        raise HTTPException(
            status_code=403,
            detail='Forbidden image format. '
            'Allowed format extensions are {}.'.format(
                settings.ALLOWED_FORMAT_EXTENSIONS
            )
        )

    image = _resize_image(file.file, size)
    image = image.convert('RGB')

    image_path = '{0}{1}.jpeg'.format(upload_path, filename)
    if os.path.exists(image_path):
        image_path = '{0}{1}_{2}.jpeg'.format(
            upload_path,
            filename,
            ''.join(sample(string.ascii_letters, 10))
        )

    image.save(image_path, 'JPEG', quality=95)
    return image_path


def _resize_image(img: SpooledTemporaryFile[bytes] | IO, size: tuple[int, int]):
    img: Image.Image = Image.open(img)
    crop: bool = not img.width / size[0] == img.height / size[1]
    if not crop:
        img.thumbnail(size, Image.ANTIALIAS)
    else:
        img = ImageOps.fit(img, size, Image.ANTIALIAS, centering=(0.5, 0.5))
    return img
