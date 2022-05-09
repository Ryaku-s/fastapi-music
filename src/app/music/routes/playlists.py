from fastapi import APIRouter, Depends, Path

from src.app.user.models import User
from src.app.base.schemas import ExceptionMessage
from src.app.music.permissions import is_user_playlist_author
from src.app.auth.permissions import get_current_active_user, token_responses
from src.app.music.models import Playlist, Track
from src.app.music.schemas import PlaylistAddTrack, PlaylistCreateForm, PlaylistOut, PlaylistUpdateForm
from src.app.music.services import PlaylistService, TrackService

playlist_router = APIRouter(prefix='/playlists', tags=['Playlists'])


@playlist_router.get('/{id}', response_model=PlaylistOut, responses={
    404: {'model': ExceptionMessage}
})
async def get_playlist(
    id: int = Path(..., description='ID of playlist')
):
    return await PlaylistService.get_object_or_404(id=id)


@playlist_router.post('', status_code=201, response_model=PlaylistOut, responses={
    201: {'description': 'A playlist'},
    **token_responses
})
async def create_playlist(
    schema: PlaylistCreateForm = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    return await PlaylistService.create(
        schema,
        author=current_user,
        duration_ms=0
    )


@playlist_router.patch('/{id}', response_model=PlaylistOut, responses={
    200: {'description': 'A playlist'},
    **token_responses
})
async def update_playlist(
    id: int = Path(..., description='ID of playlist'),
    schema: PlaylistUpdateForm = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    playlist: Playlist = await PlaylistService.get_object_or_404(id=id)

    is_user_playlist_author(current_user, playlist)

    return await PlaylistService.update(
        schema,
        id=id,
        author=current_user
    )


@playlist_router.put('/{id}/tracks', response_model=PlaylistOut, responses={
    200: {'description': 'A playlist'},
    **token_responses
})
async def add_tracks_to_playlist(
    schema: PlaylistAddTrack,
    id: int = Path(..., description='ID of playlist'),
    current_user: User = Depends(get_current_active_user)
):
    playlist: Playlist = await PlaylistService.get_object_or_404(id=id)

    is_user_playlist_author(current_user, playlist)

    async with playlist.Meta.database.connection() as conn:
        async with conn.transaction():
            for track_id in schema.tracks:
                track: Track = await TrackService.get_object_or_404(id=track_id)

                await playlist.tracks.add(track)
                await playlist.artists.add(track.artist)
                playlist.duration_ms += track.duration_ms
            await playlist.update()
    return playlist
