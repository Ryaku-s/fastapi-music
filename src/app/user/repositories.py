from src.app.base.repositories import ModelRepository
from src.app.user.models import User


class UserRepository(ModelRepository):
    _model = User
