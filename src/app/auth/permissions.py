from jose import JWTError
from fastapi import HTTPException, Security, status

from src.app.auth.http import (
    HTTPBearerAuthorization,
    HTTPAuthorizationCredentials
)
from src.app.auth.tokens import AccessToken
from src.app.base.schemas import ExceptionMessage
from src.app.user.services import UserService
from src.app.user.models import User


security = HTTPBearerAuthorization()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    token = credentials.credentials

    try:
        access_token = AccessToken(token)
        await access_token.verify()
        user_id = access_token.user_id
    except JWTError:
        raise HTTPException(
            status_code=403,
            detail='Invalid token'
        )

    user = await UserService.get_object_or_404(pk=user_id)
    return user


def get_current_active_user(user: User = Security(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Current user is inactive',
        )
    return user


def get_current_superuser(user: User = Security(get_current_user)):
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden for current user'
        )
    return user


token_responses = {
    401: {'model': ExceptionMessage, 'description': 'Bad or expired token'},
    403: {
        'model': ExceptionMessage,
        'description': 'Bad request or user doesn\'t have enough '
            'privileges'
    }
}
