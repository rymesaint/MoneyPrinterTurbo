from fastapi import Query
from app.services.youtube import youtube_service
from app.utils import utils
from app.controllers.v1.base import new_router

router = new_router()

@router.get("/youtube/status", summary="Get YouTube integration status and channel details")
def get_youtube_status():
    result = youtube_service.get_channel_info()
    return utils.get_response(200, result)

@router.get("/youtube/my-videos", summary="Retrieve uploaded videos with stats")
def get_my_videos(max_results: int = Query(default=10, ge=1, le=50)):
    result = youtube_service.get_my_videos(max_results=max_results)
    return utils.get_response(200, result)

@router.get("/youtube/video-stats", summary="Get statistics for a specific YouTube video")
def get_video_stats(video_id: str = Query(..., min_length=1)):
    result = youtube_service.get_video_stats(video_id=video_id)
    return utils.get_response(200, result)

@router.get("/youtube/trends", summary="Get YouTube trending videos")
def get_youtube_trends(
    region: str = Query(default="US", min_length=2, max_length=2),
    max_results: int = Query(default=10, ge=1, le=50)
):
    result = youtube_service.get_trending_videos(region_code=region, max_results=max_results)
    return utils.get_response(200, result)
