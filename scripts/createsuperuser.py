from getpass import getpass

import ormar

from scripts.base import CommandManager
from src.core.security import get_password_hash
from src.app.auth.schemas import UserCreate
from src.app.user.services import UserService

createsuperuser_manager = CommandManager()


@createsuperuser_manager.add_command(
    'createsuperuser',
    description='Creates superuser'
)
async def createsuperuser() -> None:
    username = input('Input superuser username: ')
    email = input('Input superuser email: ')
    password = getpass('Input superuser password: ')

    schema = UserCreate(username=username, email=email, password=password)

    exists = await UserService.exists(ormar.or_(username=username, email=email))
    if exists:
        print('User with the entered data already exists')
    else:
        await UserService.create(
            **schema.dict(exclude={'password'}),
            hashed_password=get_password_hash(schema.password)
        )
        print('Superuser has been successfully created')
