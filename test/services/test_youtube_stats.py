from unittest.mock import MagicMock, patch
from app.services.youtube import youtube_service
from app.controllers.v1.youtube import router

def test_youtube_service_is_configured():
    is_conf = youtube_service.is_configured()
    assert isinstance(is_conf, bool)

def test_get_channel_info_unconfigured():
    with patch.object(youtube_service, 'is_configured', return_value=False):
        res = youtube_service.get_channel_info()
        assert res["success"] is False
        assert "not configured" in res["error"]

def test_get_my_videos_unconfigured():
    with patch.object(youtube_service, 'is_configured', return_value=False):
        res = youtube_service.get_my_videos()
        assert res["success"] is False
        assert "not configured" in res["error"]

def test_get_video_stats_unconfigured():
    with patch.object(youtube_service, 'is_configured', return_value=False):
        res = youtube_service.get_video_stats("some_id")
        assert res["success"] is False
        assert "not configured" in res["error"]

def test_get_trending_videos_unconfigured():
    with patch.object(youtube_service, 'is_configured', return_value=False):
        res = youtube_service.get_trending_videos()
        assert res["success"] is False
        assert "not configured" in res["error"]

if __name__ == "__main__":
    test_youtube_service_is_configured()
    test_get_channel_info_unconfigured()
    test_get_my_videos_unconfigured()
    test_get_video_stats_unconfigured()
    test_get_trending_videos_unconfigured()
    print("All tests passed successfully!")
