from fastapi import UploadFile
from pydantic import BaseModel


class UserUpdate(BaseModel):
    avatar: UploadFile | None = None
    about: str | None = None
