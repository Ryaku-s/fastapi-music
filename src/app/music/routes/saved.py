from fastapi import APIRouter, Depends, Path, Query, Request, Response

from src.app.base.paginator import paginate
from src.app.base.schemas import Message
from src.app.auth.permissions import get_current_active_user, token_responses
from src.app.user.models import User
from src.app.music import schemas, services


saved_router = APIRouter(prefix='/users/me/saved')

@saved_router.get(
    '/tracks',
    response_model=schemas.TrackList,
    tags=['Tracks'],
    responses={
        200: {'description': 'Pages of tracks'},
        **token_responses
    }
)
async def get_saved_tracks(
    request: Request,
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50),
    current_user: User = Depends(get_current_active_user)
):
    return await services.SavedTrackService.get_pages(
        offset,
        limit,
        request.url,
        user=current_user
    )


@saved_router.put(
    '/tracks',
    response_model=Message,
    tags=['Tracks'],
    responses=token_responses
)
async def save_track(
    schema: schemas.TrackSave,
    current_user: User = Depends(get_current_active_user)
):
    track = await services.TrackService.get_object_or_404(id=schema.id)
    await services.SavedTrackService.get_or_create(
        track=track,
        user=current_user
    )
    return Message(msg='Track saved successfully')


@saved_router.delete(
    '/tracks/{id}',
    status_code=204,
    tags=['Tracks'],
    response_class=Response,
    responses=token_responses
)
async def remove_saved_track(
    id: int = Path(..., gt=0, description='ID of track'),
    current_user: User = Depends(get_current_active_user)
):
    await services.SavedTrackService.delete(
        user=current_user.id,
        track=id
    )


@saved_router.get(
    '/albums',
    response_model=schemas.AlbumList,
    tags=['Albums'],
    responses={
        200: {'description': 'Pages of albums'},
        **token_responses
    }
)
async def get_saved_albums(
    request: Request,
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50),
    current_user: User = Depends(get_current_active_user)
):
    return await services.SavedAlbumService.get_pages(
        offset,
        limit,
        request.url,
        user=current_user
    )


@saved_router.put(
    '/albums',
    response_model=Message,
    tags=['Albums'],
    responses=token_responses
)
async def save_album(
    schema: schemas.AlbumSave,
    current_user: User = Depends(get_current_active_user)
):
    album = await services.AlbumService.get_object_or_404(id=schema.id)
    await services.SavedAlbumService.get_or_create(
        album=album,
        user=current_user
    )
    return Message(msg='Album saved successfully')


@saved_router.delete(
    '/albums/{id}',
    status_code=204,
    tags=['Albums'],
    response_class=Response,
    responses=token_responses
)
async def remove_saved_album(
    id: int = Path(..., gt=0, description='ID of album'),
    current_user: User = Depends(get_current_active_user)
):
    await services.SavedAlbumService.delete(
        user=current_user.id,
        album=id
    )
