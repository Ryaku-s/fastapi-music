from fastapi import APIRouter, Path, Query, Request
from src.app.base.paginator import paginate

from src.app.music import schemas, services
from src.app.base.schemas import ExceptionMessage


track_router = APIRouter(prefix='/tracks', tags=['Tracks'])


@track_router.get('', response_model=schemas.TrackList, responses={
    200: {'description': 'Pages of tracks'}
})
async def get_tracks(
    request: Request,
    offset: int = Query(0, ge=0, le=100000),
    limit: int = Query(15, ge=0, le=50)
):
    return await services.TrackService.get_pages(
        offset,
        limit,
        request.url
    )


@track_router.get('/{id}', response_model=schemas.TrackOut, responses={
    200: {'description': 'A track'},
    404: {'model': ExceptionMessage}
})
async def get_single_track(id: int = Path(..., gt=0)):
    return await services.TrackService.get_object_or_404(id=id)
