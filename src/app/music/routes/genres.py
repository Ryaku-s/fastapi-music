from fastapi import APIRouter, Depends

from src.app.music import models, schemas, services
from src.app.auth.permissions import get_current_superuser, token_responses


genre_router = APIRouter(prefix='/genres', tags=['Genres'])


@genre_router.post(
    '',
    status_code=201,
    response_model=models.Genre,
    dependencies=[Depends(get_current_superuser)],
    responses=token_responses
)
async def create_genre(schema: schemas.Genre):
    return await services.GenreService.create(schema)
