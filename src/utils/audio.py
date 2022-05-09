import os
import string
from random import sample

from mutagen.mp3 import MP3
from fastapi import HTTPException, UploadFile

from src.config import settings


def _get_audio_duration(file_path: str) -> int:
    audio = MP3(file_path)
    return int(audio.info.length * 1000)


async def upload_audio(upload_path: str, file: UploadFile) -> tuple[str, int]:
    filename, extension = file.filename.split('.')

    if extension not in settings.ALLOWED_AUDIO_FORMAT_EXTENSIONS:
        raise HTTPException(
            status_code=403,
            detail='Forbidden image format. '
            'Allowed format extension is {}.'.format(', '.join(
                settings.ALLOWED_AUDIO_FORMAT_EXTENSIONS
            ))
        )

    file_path = '{}{}'.format(upload_path, file.filename)

    if os.path.exists(file_path):
        file_path = '{0}{1}_{2}.mp3'.format(
            upload_path,
            filename,
            ''.join(sample(string.ascii_letters, 10))
        )

    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)

    duration_ms = _get_audio_duration(file_path)

    return file_path, duration_ms
