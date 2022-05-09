from typing import Type

from ormar import Model

from src.app.base.services import ModelService
from src.app.user.models import User


class UserService(ModelService):
    model: Type[Model] = User
