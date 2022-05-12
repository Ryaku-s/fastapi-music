from datetime import datetime

import ormar
from fastapi import BackgroundTasks, HTTPException

from src.app.auth.tokens import (
    AccessToken,
    EmailConfirmationToken,
    PasswordResetToken,
    RefreshToken
)
from src.app.user.models import User
from src.app.user.services import UserService
from src.app.auth.jwt import generate_refresh_token
from src.config import settings
from src.core.security import get_password_hash, verify_password
from src.app.auth.schemas import PasswordChange, UserCreate, UserLogin
from src.utils.email import send_email_confirmation, send_password_reset


async def register_user(user: UserCreate, task: BackgroundTasks) -> None:
    user_exists = await User.objects.filter(
        ormar.or_(username=user.username, email=user.email)
    ).exists()

    if user_exists:
        raise HTTPException(
            status_code=400,
            detail='User with the entered data already exists'
        )

    user_db = await UserService.create(
        **user.dict(exclude={'password'}),
        hashed_password=get_password_hash(user.password)
    )

    task.add_task(
        send_email_confirmation, user_db
    )


async def confirm_user_email(token: str):
    email_confirmation_token = EmailConfirmationToken(token)
    user: User = await email_confirmation_token.verify()

    await user.update(email_confirmed=True)


async def authenticate_user(schema: UserLogin) -> User:
    user: User = await UserService.get_object_or_none(username=schema.username)

    if not user or not verify_password(schema.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )

    if not user.email_confirmed and not user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='Email not confirmed'
        )

    return user


async def logout_user_from_all_devices(token: str) -> None:
    access_token = AccessToken(token)
    user = await access_token.verify()

    await user.update(invalidate_before=datetime.utcnow())


async def change_user_password(token: str, schema: PasswordChange) -> None:
    access_token = AccessToken(token)
    user = await access_token.verify()

    if not verify_password(schema.raw_old_password, user.hashed_password):
        raise HTTPException(
            status_code=403,
            detail='Wrong old password'
        )

    new_hashed_password = get_password_hash(schema.raw_new_password)
    await user.update(
        hashed_password=new_hashed_password,
        invalidate_before=datetime.utcnow()
    )


async def refresh_access_token(token: str) -> dict:
    refresh_token = RefreshToken(token)
    user: User = await refresh_token.verify()

    new_access_token = refresh_token.refresh_access_token()
    new_refresh_token = generate_refresh_token(user.id)

    return {
        'access_token': new_access_token,
        'expires_in': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        'refresh_token': new_refresh_token,
        'refresh_token_expires_in': settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    }


async def recover_user_password(email: str, task: BackgroundTasks) -> None:
    user = await UserService.get_object_or_404(email=email)

    task.add_task(
        send_password_reset, user
    )


async def reset_user_password(token: str, new_raw_password: str) -> None:
    user: User = await PasswordResetToken(token).verify()
    new_hashed_password = get_password_hash(new_raw_password)

    await user.update(
        hashed_password=new_hashed_password,
        invalidate_before=datetime.utcnow()
    )
