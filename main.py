from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from scripts.base import command_manager
from src.config import settings
from src.core.db import database
from src.app.routers import app_router

app = FastAPI(
    title='FastAPI Music',
    description='Fast API Music\'s REST API',
    docs_url='{}/swagger'.format(settings.API_V1_PREFIX),
    redoc_url='{}/docs'.format(settings.API_V1_PREFIX)
)

app.mount('/media', StaticFiles(directory='media'), name='media')
app.state.database = database


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(app_router)


if __name__ == '__main__':
    args = command_manager.parse_args()
    args.func(args)
