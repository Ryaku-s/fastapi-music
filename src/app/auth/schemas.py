from fastapi import Body
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    password: str = Body(..., min_length=8, max_length=72)


class UserLogin(UserBase):
    pass


class UserCreate(UserLogin):
    email: EmailStr


class AuthTokens(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_token_expires_in: int


class Token(BaseModel):
    token: str


class RefreshToken(Token):
    token: str


class EmailConfirmationToken(Token):
    token: str


class PasswordResetToken(Token):
    token: str


class Email(BaseModel):
    email: EmailStr


class PasswordRecovery(Email):
    pass


class PasswordReset(PasswordResetToken):
    new_password: str


class PasswordChange(PasswordReset):
    old_password: str
