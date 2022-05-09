from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from pydantic import EmailStr

from src.config import settings
from src.app.auth.jwt import generate_email_confirmation_token, generate_password_reset_token
from src.app.user.models import User

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
    TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)


async def _send_mail(email: EmailStr, subject: str, body: dict, template_name: str) -> None:
    message = MessageSchema(
        recipients=[email],
        subject=subject,
        template_body=body,
        subtype='html'
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name=template_name)


async def send_email_confirmation(user: User) -> None:
    token = generate_email_confirmation_token(user.id)
    body = {
        'username': user.username,
        'link': 'http://{0}/link-example/?token={1}'.format(settings.SITE_DOMAIN, token)
    }
    await _send_mail(
        user.email,
        '[FastAPI Music] Confirm E-mail',
        body,
        'email_confirmation.html'
    )


async def send_password_reset(user: User) -> None:
    token = generate_password_reset_token(user.id)
    body = {
        'link': 'http://{0}/link-example/?token={1}'.format(settings.SITE_DOMAIN, token)
    }
    await _send_mail(
        user.email,
        '[FastAPI Music] Password Reset',
        body,
        'password_reset.html'
    )
