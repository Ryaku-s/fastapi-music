from datetime import datetime, timezone

from jose import jwt, JWTError
from fastapi import HTTPException

from src.config import settings
from src.app.user.models import User
from src.app.user.services import UserService
from src.app.auth.jwt import generate_access_token


class Token:
    _token_type: str = None
    _secret_key: str = None

    def __init__(self, token: str) -> None:
        self._token = token

        if self._secret_key:
            try:
                self._payload = jwt.decode(
                    token, self._secret_key, settings.ALGORITHM
                )
            except JWTError:
                raise HTTPException(status_code=403, detail='Invalid token')
        else:
            self._payload = {}

    @property
    def user_id(self):
        return int(self._get_sub())

    async def verify(self) -> User:
        user: User = await UserService.get_object_or_404(pk=self.user_id)

        if (not self._is_token_type_valid() or
                not self._is_iat_valid(user.invalidate_before)):
            raise HTTPException(status_code=403, detail='Invalid token')

        return user

    def _get(self, key) -> str:
        try:
            val = self._payload[key]
        except KeyError:
            raise HTTPException(status_code=403, detail='Invalid token')

        return val

    def _get_token_type(self) -> str:
        return self._get('token_type')

    def _get_exp(self) -> str:
        return self._get('exp')

    def _get_sub(self) -> str:
        return self._get('sub')

    def _get_iat(self) -> str:
        return self._get('iat')

    def _is_token_type_valid(self) -> bool:
        return self._get_token_type() == self._token_type

    def _is_iat_valid(self, invalidate_before: datetime) -> bool:
        iat_datetime = datetime.fromtimestamp(self._get_iat(), timezone.utc)\
            .replace(tzinfo=None)
        return invalidate_before <= iat_datetime


class AccessToken(Token):
    _token_type: str = settings.ACCESS_TOKEN_TYPE
    _secret_key: str = settings.ACCESS_TOKEN_SECRET_KEY


class RefreshToken(Token):
    _token_type: str = settings.REFRESH_TOKEN_TYPE
    _secret_key: str = settings.REFRESH_TOKEN_SECRET_KEY

    def refresh_access_token(self) -> str:
        user_id = self.user_id
        return generate_access_token(user_id)


class EmailConfirmationToken(Token):
    _token_type: str = settings.EMAIL_CONFIRMATION_TOKEN_TYPE
    _secret_key: str = settings.EMAIL_CONFIRMATION_TOKEN_SECRET_KEY


class PasswordResetToken(Token):
    _token_type: str = settings.PASSWORD_RESET_TOKEN_TYPE
    _secret_key: str = settings.PASSWORD_RESET_TOKEN_SECRET_KEY
