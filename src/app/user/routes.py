import os

from fastapi import APIRouter, Depends

from src.utils.image import upload_image
from src.app.user.models import User
from src.app.user.schemas import UserUpdate
from src.app.auth.permissions import get_current_active_user
from src.app.base.uploads import get_avatar_upload_path
from src.app.base.schemas import ExceptionMessage


user_router = APIRouter(tags=['Users'])


@user_router.get('/me', response_model=User, responses={
    200: {'description': 'An user'},
    401: {
        'model': ExceptionMessage,
        'description': 'Bad or expired token'
    },
    403: {
        'model': ExceptionMessage,
        'description': 'Bad request or user doesn\'t have enough '
            'privileges'
    }
})
async def get_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user



@user_router.patch('/me', response_model=User, responses={
    200: {'description': 'An user'},
    401: {
        'model': ExceptionMessage,
        'description': 'Bad or expired token'
    },
    403: {
        'model': ExceptionMessage,
        'description': 'Bad request or user doesn\'t have enough '
            'privileges'
    }
})
async def update_current_user(schema: UserUpdate, current_user: User = Depends(get_current_active_user)):
    avatar = schema.avatar
    if avatar:
        upload_path = get_avatar_upload_path()
        os.makedirs(upload_path, exist_ok=True)

        image_path = upload_image(upload_path, avatar, (250, 250))
        avatar = image_path

    return await current_user.update(avatar=avatar, about=schema.about)
