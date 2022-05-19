from fastapi import APIRouter, Depends, Path, Response

from src.app.music import models, schemas, services
from src.app.auth.permissions import get_current_superuser, token_responses


genre_router = APIRouter(prefix='/genres', tags=['Genres'])


@genre_router.get('', response_model=list[str], responses={
    200: {
        'description': 'An array of genres'
    }
})
async def get_genres():
    return [genre.title for genre in await services.GenreService.all()]


@genre_router.post(
    '',
    status_code=201,
    response_model=models.Genre,
    dependencies=[Depends(get_current_superuser)],
    responses=token_responses
)
async def create_genre(schema: schemas.Genre):
    return await services.GenreService.create(schema)


@genre_router.put(
    '/{id}',
    status_code=201,
    response_model=models.Genre,
    dependencies=[Depends(get_current_superuser)],
    responses=token_responses
)
async def update_genre(
    schema: schemas.Genre,
    id: int = Path(..., description='ID of genre')
):
    return await services.GenreService.update(schema, id=id)


@genre_router.delete(
    '/{id}',
    status_code=201,
    response_model=models.Genre,
    dependencies=[Depends(get_current_superuser)],
    responses=token_responses,
    response_class=Response
)
async def delete_genre(
    id: int = Path(..., description='ID of genre')
):
    return await services.GenreService.delete(id=id)
