from fastapi import APIRouter

from src.app.auth.routes import auth_router
from src.app.user.routes import user_router
from src.app.music.routes import (
    album_router,
    track_router,
    genre_router,
    saved_router,
    playlist_router
)
from src.config.settings import API_V1_PREFIX


app_router = APIRouter(prefix=API_V1_PREFIX)

app_router.include_router(album_router)
app_router.include_router(track_router)
app_router.include_router(playlist_router)
app_router.include_router(genre_router)
app_router.include_router(saved_router)
app_router.include_router(auth_router)
app_router.include_router(user_router)
