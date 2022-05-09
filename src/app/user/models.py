from datetime import datetime

import ormar
from sqlalchemy import func

from src.core.db import BaseMeta


class User(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=100, nullable=False, unique=True)
    email: str = ormar.String(max_length=256, nullable=False, unique=True)
    email_confirmed: bool = ormar.Boolean(default=False, nullable=False)
    hashed_password: str = ormar.String(max_length=1000, nullable=False)
    avatar: str | None = ormar.String(max_length=255, nullable=True)
    about: str | None = ormar.Text(max_length=2000, nullable=True)
    date_joined: datetime = ormar.DateTime(server_default=func.now())
    is_active: bool = ormar.Boolean(default=True, nullable=False)
    invalidate_before: datetime = ormar.DateTime(server_default=func.now())
    is_superuser: bool = ormar.Boolean(default=False, nullable=False)
