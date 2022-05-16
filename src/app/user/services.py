from src.app.base.services import ModelService
from src.app.user.repositories import UserRepository


class UserService(ModelService):
    _repository = UserRepository
