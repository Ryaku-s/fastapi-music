from pydantic import EmailStr
from fastapi import APIRouter, BackgroundTasks, Security
from fastapi.security import HTTPAuthorizationCredentials

from src.config import settings
from src.app.base.schemas import Message, ExceptionMessage
from src.app.auth.permissions import security, token_responses
from src.app.auth.jwt import generate_access_token, generate_refresh_token
from src.app.auth import schemas, services

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post('/user', response_model=Message, responses={
    404: {'model': ExceptionMessage}
})
async def register(user: schemas.UserCreate, task: BackgroundTasks):
    await services.register_user(user, task)
    return Message(msg='Email confirmation has been sent')


@auth_router.post(
    '/token',
    response_model=schemas.AuthTokens,
    responses=token_responses
)
async def login(schema: schemas.UserLogin):
    user = await services.authenticate_user(schema)

    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)

    return {
        'access_token': access_token,
        'expires_in': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        'refresh_token': refresh_token,
        'refresh_token_expires_in': settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    }


@auth_router.put('/token', response_model=schemas.AuthTokens, responses= {
    403: {
        'model': ExceptionMessage,
        'description': 'Bad request or user doesn\'t have enough '
            'privileges'
    }
})
async def refresh(schema: schemas.RefreshToken):
    return await services.refresh_access_token(schema.token)


@auth_router.post(
    '/devices/logout',
    status_code=204,
    responses={
        204: {
            'description': 'Successful logout from all devices'
        },
        **token_responses
    }
)
async def logout_from_all_devices(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    await services.logout_user_from_all_devices(token)


@auth_router.put(
    '/email',
    status_code=204,
    responses= {
        204: {
            'description': 'Email confirmed successfully'
        },
        403: {
            'model': ExceptionMessage,
            'description': 'Bad request or user doesn\'t have enough '
                'privileges'
        }
    }
)
async def confirm_email(schema: schemas.EmailConfirmationToken):
    await services.confirm_user_email(schema.token)


@auth_router.post(
    '/password',
    status_code=204,
    responses= {
        204: {
            'description': 'Password changed successfully'
        },
        403: {
            'model': ExceptionMessage,
            'description': 'Bad request or user doesn\'t have enough '
                'privileges'
        }
    }
)
async def reset_password(schema: schemas.PasswordReset):
    await services.reset_user_password(
        schema.token,
        schema.new_password
    )


@auth_router.put(
    '/password',
    status_code=204,
    responses={
        204: {
            'description': 'Password changed successfully'
        },
        **token_responses
    }
)
async def change_password(
    passwords: schemas.PasswordChange,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    await services.change_user_password(
        token,
        passwords.old_password,
        passwords.new_password
    )


@auth_router.post(
    '/password/recovery',
    status_code=204,
    responses={
        204: {
            'description': 'Password reset mail has been sent'
        },
        404: {'model': ExceptionMessage}
    }
)
async def recover_password(
    schema: schemas.PasswordRecovery,
    task: BackgroundTasks
):
    await services.recover_user_password(schema.email, task)
    return Message(msg='Password reset mail has been sent')
