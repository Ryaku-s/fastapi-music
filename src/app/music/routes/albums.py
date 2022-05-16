from fastapi import APIRouter, Depends, Path, Query, Request, Response
from starlette.datastructures import URL

from src.app.base.paginator import paginate
from src.app.base.schemas import ExceptionMessage
from src.app.auth.permissions import get_current_active_user, token_responses
from src.app.user.models import User
from src.app.music import models, schemas, services
from src.app.music.permissions import (
    is_user_album_author,
    is_user_track_author
)

album_router = APIRouter(prefix='/albums', tags=['Albums'])


@album_router.get('', response_model=schemas.AlbumList, responses={
    200: {'description': 'Pages of albums'}
})
async def get_albums(
    request: Request,
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50)
):
    return await services.AlbumService.get_pages(offset, limit, request.url)


@album_router.get('/{id}', response_model=schemas.AlbumOut, responses={
    200: {'description': 'An album'},
    404: {'model': ExceptionMessage}
})
async def get_single_album(
    id: int = Path(..., gt=0, description='ID of album')
):
    album = await services.AlbumService.get_object_or_404(id=id)
    tracks = await services.TrackService.get_pages(
        0,
        15,
        URL('http://127.0.0.1:8000/api/v1/albums/{}/tracks?offset=0&limit=15'\
            .format(id)),
        album__id=album.id
    )
    return {
        **album.dict(exclude={'tracks'}),
        'tracks': tracks
    }


@album_router.post(
    '',
    status_code=201,
    response_model=schemas.AlbumOut,
    dependencies=[Depends(get_current_active_user)],
    responses={
        201: {'description': 'An album'},
        **token_responses
    }
)
async def create_album(
    schema: schemas.AlbumCreateForm = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    return await services.AlbumService.create(schema, artist=current_user)


@album_router.patch(
    '/{id}',
    status_code=204,
    responses={
        204: {'description': 'Album updated'},
        **token_responses,
        404: {'model': ExceptionMessage}
    },
    response_class=Response
)
async def update_album(
    id: int = Path(..., gt=0, description='ID of album'),
    schema: schemas.AlbumUpdateForm = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    album = await services.AlbumService.get_object_or_404(id=id)
    is_user_album_author(current_user, album)
    await services.AlbumService.update(schema, id=id)


@album_router.delete(
    '/{id}',
    status_code=204,
    response_class=Response,
    responses=token_responses
)
async def delete_album(
    id: int = Path(..., gt=0, description='ID of album'),
    current_user: User = Depends(get_current_active_user)
):
    album = await services.AlbumService.get_object_or_404(id=id)
    is_user_album_author(current_user, album)
    await album.delete()


@album_router.get(
    '/{album_id}/tracks',
    response_model=schemas.TrackList,
    responses={
        200: {'description': 'Pages of tracks'}
    }
)
async def get_album_tracks(
    request: Request,
    album_id: int = Path(..., gt=0),
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50)
):
    return await services.TrackService.get_pages(
        offset,
        limit,
        request.url,
        album__id=album_id
    )


@album_router.post(
    '/{album_id}/tracks',
    status_code=201,
    response_model=schemas.TrackOut,
    responses={
        201: {'description': 'A track'},
        **token_responses
    }
)
async def upload_track_to_album(
    schema: schemas.TrackCreateForm = Depends(),
    album_id: int = Path(..., gt=0, description='ID of album'),
    current_user: User = Depends(get_current_active_user)
):
    album: models.Album = await services.AlbumService.get_object_or_404(
        id=album_id
    )

    is_user_album_author(current_user, album)

    await services.AlbumService.is_available_to_upload(album)
    async with album.Meta.database.connection() as conn:
        async with conn.transaction():
            track = await services.TrackService.create(
                schema,
                album=album,
                artist=current_user
            )
            await album.update(
                duration_ms=album.duration_ms + track.duration_ms
            )

    return track


@album_router.patch(
    '/{album_id}/tracks/{id}',
    response_model=schemas.TrackOut,
    responses={
        201: {'description': 'A track'},
        **token_responses
    }
)
async def update_album_track(
    schema: schemas.TrackUpdateForm = Depends(),
    album_id: int = Path(..., gt=0, description='ID of album'),
    id: int = Path(..., gt=0, description='ID of track'),
    current_user: User = Depends(get_current_active_user)
):
    album: models.Album = await services.AlbumService.get_object_or_404(
        id=album_id
    )

    is_user_album_author(current_user, album)

    async with album.Meta.database.connection() as conn:
        async with conn.transaction():
            track = await services.TrackService.update(
                schema,
                id=id,
                artist=current_user.id
            )
            await album.update(
                duration_ms=album.duration_ms + track.duration_ms
            )

    return track


@album_router.delete(
    '/{album_id}/tracks/{id}',
    status_code=204,
    response_class=Response,
    responses=token_responses
)
async def delete_album_track(
    album_id: int = Path(..., gt=0, description='ID of album'),
    id: int = Path(..., gt=0, description='ID of track'),
    current_user: User = Depends(get_current_active_user)
):
    track = await services.TrackService.get_object_or_404(
        id=id,
        album_id=album_id
    )
    is_user_track_author(current_user, track)
    await track.delete()
