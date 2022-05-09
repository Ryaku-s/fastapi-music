from datetime import datetime, timedelta

from jose import jwt

from src.config import settings


def _generate_typed_token(
    subject: str,
    token_type: str,
    lifetime: timedelta,
    secret: str,
    algorithm: str,
    **payload
) -> str:
    expires_at = datetime.utcnow() + lifetime

    to_encode = payload.copy()

    to_encode['sub'] = subject
    to_encode['token_type'] = token_type
    to_encode['exp'] = expires_at
    to_encode['iat'] = datetime.utcnow()
    return jwt.encode(to_encode, secret, algorithm)


def generate_access_token(
    user_id: int,
    algorithm: str = settings.ALGORITHM
) -> str:
    lifetime = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _generate_typed_token(
        str(user_id),
        settings.ACCESS_TOKEN_TYPE,
        lifetime,
        settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm
    )


def generate_refresh_token(
    user_id: int,
    algorithm: str = settings.ALGORITHM
) -> str:
    lifetime = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return _generate_typed_token(
        str(user_id),
        settings.REFRESH_TOKEN_TYPE,
        lifetime,
        settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm
    )


def generate_email_confirmation_token(
    user_id: int,
    algorithm: str = settings.ALGORITHM
) -> str:
    lifetime = timedelta(minutes=settings.EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES)
    return _generate_typed_token(
        str(user_id),
        settings.EMAIL_CONFIRMATION_TOKEN_TYPE,
        lifetime,
        settings.EMAIL_CONFIRMATION_TOKEN_SECRET_KEY,
        algorithm
    )


def generate_password_reset_token(
    user_id: int,
    algorithm: str = settings.ALGORITHM
) -> str:
    lifetime = timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    return _generate_typed_token(
        str(user_id),
        settings.PASSWORD_RESET_TOKEN_TYPE,
        lifetime,
        settings.PASSWORD_RESET_TOKEN_SECRET_KEY,
        algorithm
    )
