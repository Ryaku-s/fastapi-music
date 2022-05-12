from fastapi import APIRouter, Depends, Path, Query, Request, Response
from starlette.datastructures import URL

from src.app.base.schemas import ExceptionMessage
from src.app.base.paginator import paginate
from src.app.auth.permissions import get_current_active_user, token_responses
from src.app.user.models import User
from src.app.music import schemas
from src.app.music.models import Playlist, Track
from src.app.music.permissions import is_user_playlist_author
from src.app.music.services import PlaylistService, TrackService

playlist_router = APIRouter(prefix='/playlists', tags=['Playlists'])


@playlist_router.get('', response_model=schemas.PlaylistList, responses={
    200: {'description': 'Pages of albums'}
})
async def get_playlists(
    request: Request,
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50)
):
    return await PlaylistService.get_pages(offset, limit, request.url)


@playlist_router.get('/{id}', response_model=schemas.PlaylistOut, responses={
    404: {'model': ExceptionMessage}
})
async def get_single_playlist(
    id: int = Path(..., description='ID of playlist')
):
    playlist = await PlaylistService.get_object_or_404(id=id)
    tracks = paginate(
        playlist.tracks,
        0,
        15,
        URL('http://127.0.0.1:8000/api/v1/playlists/{}/tracks'
                '?offset=0&limit=15'.format(id))
    )
    return {
        **playlist.dict(exclude={'tracks'}),
        'tracks': tracks
    }


@playlist_router.post(
    '',
    status_code=201,
    response_model=schemas.PlaylistOut,
    responses={
        201: {'description': 'A playlist'},
        **token_responses
    }
)
async def create_playlist(
    schema: schemas.PlaylistCreateForm = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    return await PlaylistService.create(
        schema,
        author=current_user,
        duration_ms=0
    )


@playlist_router.patch('/{id}', response_model=schemas.PlaylistOut, responses={
    200: {'description': 'A playlist'},
    **token_responses
})
async def update_playlist(
    id: int = Path(..., description='ID of playlist'),
    schema: schemas.PlaylistUpdateForm = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    playlist: Playlist = await PlaylistService.get_object_or_404(id=id)

    is_user_playlist_author(current_user, playlist)

    return await PlaylistService.update(
        schema,
        id=id,
        author=current_user
    )


@playlist_router.delete(
    '/{id}',
    status_code=204,
    response_class=Response,
    responses=token_responses
)
async def delete_playlist(
    id: int = Path(..., gt=0, description='ID of album'),
    current_user: User = Depends(get_current_active_user)
):
    playlist = await PlaylistService.get_object_or_404(id=id)
    is_user_playlist_author(current_user, playlist)
    await playlist.delete()


@playlist_router.get(
    '/{playlist_id}/tracks',
    response_model=schemas.TrackList,
    responses={
        200: {'description': 'Pages of tracks'}
    }
)
async def get_album_tracks(
    request: Request,
    playlist_id: int = Path(..., gt=0),
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50)
):
    playlist = await PlaylistService.get_object_or_404(id=playlist_id)
    return paginate(playlist.tracks, offset, limit, request.url)


@playlist_router.put(
    '/{playlist_id}/tracks',
    response_model=schemas.PlaylistOut,
    responses={
        204: {
            'description': 'Tracks added to playlist successfully'
        },
        **token_responses
    },
    response_class=Response
)
async def add_tracks_to_playlist(
    schema: schemas.PlaylistAddTrack,
    playlist_id: int = Path(..., description='ID of playlist'),
    current_user: User = Depends(get_current_active_user)
):
    playlist: Playlist = await PlaylistService.get_object_or_404(
        id=playlist_id
    )

    is_user_playlist_author(current_user, playlist)

    async with playlist.Meta.database.connection() as conn:
        async with conn.transaction():
            for track_id in schema.tracks:
                track: Track = await TrackService.get_object_or_404(
                    id=track_id
                )

                await playlist.tracks.add(track)
                await playlist.artists.add(track.artist)
                playlist.duration_ms += track.duration_ms
            await playlist.update()


@playlist_router.delete(
    '/{playlist_id}/tracks',
    status_code=204,
    response_class=Response,
    responses=token_responses
)
async def remove_playlist_tracks(
    schema: schemas.PlaylistAddTrack,
    playlist_id: int = Path(..., gt=0, description='ID of track'),
    current_user: User = Depends(get_current_active_user)
):
    playlist: Playlist = await PlaylistService.get_object_or_404(
        id=playlist_id
    )
    is_user_playlist_author(current_user, playlist)

    for track_id in schema.tracks:
        exist = 0 not in (
            await playlist.Meta.database.fetch_one(
                f'''SELECT EXISTS(SELECT id FROM playlists_tracks
                        WHERE track={track_id} and playlist={playlist_id})'''
                )
            )
        if exist:
            track = await TrackService.get_object_or_404(id=track_id)
            await playlist.tracks.remove(track)
