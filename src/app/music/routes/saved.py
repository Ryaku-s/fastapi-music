from fastapi import APIRouter, Depends, Path, Query, Request, Response

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
    tags=['Tracks'],
    status_code=204,
    responses={
        204: {'description': 'Track saved successfully'},
        **token_responses
    },
    response_class=Response
)
async def save_track(
    schema: schemas.TrackId,
    current_user: User = Depends(get_current_active_user)
):
    track = await services.TrackService.get_object_or_404(id=schema.id)
    await services.SavedTrackService.get_or_create(
        track=track,
        user=current_user
    )


@saved_router.delete(
    '/tracks',
    status_code=204,
    tags=['Tracks'],
    responses=token_responses,
    response_class=Response
)
async def remove_saved_track(
    schema: schemas.TrackId,
    current_user: User = Depends(get_current_active_user)
):
    await services.SavedTrackService.delete(
        user=current_user.id,
        track=schema.id
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
    tags=['Albums'],
    status_code=204,
    responses={
        204: {'description': 'Album saved successfully'},
        **token_responses
    },
    response_class=Response
)
async def save_album(
    schema: schemas.AlbumId,
    current_user: User = Depends(get_current_active_user)
):
    album = await services.AlbumService.get_object_or_404(id=schema.id)
    await services.SavedAlbumService.get_or_create(
        album=album,
        user=current_user
    )


@saved_router.delete(
    '/albums',
    status_code=204,
    tags=['Albums'],
    responses=token_responses,
    response_class=Response
)
async def remove_saved_album(
    schema: schemas.AlbumId,
    current_user: User = Depends(get_current_active_user)
):
    await services.SavedAlbumService.delete(
        user=current_user.id,
        album=schema.id
    )


@saved_router.get(
    '/playlists',
    tags=['Playlists']
)
async def get_saved_playlsits(
    request: Request,
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50),
    current_user: User = Depends(get_current_active_user)
):
    return await services.SavedPlaylistService.get_pages(
        offset,
        limit,
        request.url,
        user=current_user
    )


@saved_router.put(
    '/playlists',
    response_model=Message,
    tags=['Playlists'],
    responses={
        200: {'description': 'Playlist saved successfully'},
        **token_responses
    },
    response_class=Response
)
async def save_playlist(
    schema: schemas.PlaylistId,
    current_user: User = Depends(get_current_active_user)
):
    playlist = await services.PlaylistService.get_object_or_404(id=schema.id)
    await services.SavedPlaylistService.get_or_create(
        playlist=playlist,
        user=current_user
    )


@saved_router.delete(
    '/playlists',
    status_code=204,
    tags=['Playlists'],
    responses=token_responses,
    response_class=Response
)
async def remove_saved_playlist(
    schema: schemas.PlaylistId,
    current_user: User = Depends(get_current_active_user)
):
    await services.SavedAlbumService.delete(
        user=current_user.id,
        album=schema.id
    )
