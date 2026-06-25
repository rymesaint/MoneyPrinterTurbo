import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.facebook import FacebookService


_CONFIG_BASE = {
    "enabled": True,
    "page_id": "test_page_123",
    "access_token": "test_token_abc",
    "api_version": "v20.0",
}


def _mock_json_response(data, status_code=200):
    r = MagicMock()
    r.json.return_value = data
    r.status_code = status_code
    r.text = str(data)
    r.raise_for_status = MagicMock()
    return r


class TestFacebookReelsUpload(unittest.TestCase):

    @patch("app.services.facebook.config.facebook", _CONFIG_BASE)
    @patch("app.services.facebook.os.path.exists", return_value=True)
    @patch("app.services.facebook.os.path.getsize", return_value=12345)
    @patch("builtins.open", mock_open(read_data=b"fake_video_bytes"))
    @patch("app.services.facebook.requests.post")
    def test_upload_reel_success(self, mock_post, _getsize, _exists):
        # We need mock responses for three POST requests:
        # 1. Start phase
        # 2. Upload binary phase
        # 3. Finish phase
        mock_post.side_effect = [
            _mock_json_response({"video_id": "fb_video_789", "upload_url": "https://rupload.fb.com/upload"}),
            _mock_json_response({"success": True}),
            _mock_json_response({"success": True, "id": "reel_published_999"})
        ]

        svc = FacebookService()
        result = svc.upload_reel("/fake/path.mp4", "Check out OtakKepo! #viral")

        self.assertTrue(result["success"])
        self.assertEqual(result["video_id"], "reel_published_999")
        self.assertEqual(mock_post.call_count, 3)

        # Verify call arguments
        # Step 1: Start Call
        first_call_args, first_call_kwargs = mock_post.call_args_list[0]
        self.assertIn("video_reels", first_call_args[0])
        self.assertEqual(first_call_kwargs["params"]["upload_phase"], "start")
        self.assertEqual(first_call_kwargs["params"]["access_token"], "test_token_abc")

        # Step 2: Upload Binary Call
        second_call_args, second_call_kwargs = mock_post.call_args_list[1]
        self.assertEqual(second_call_args[0], "https://rupload.fb.com/upload")
        self.assertEqual(second_call_kwargs["headers"]["Authorization"], "OAuth test_token_abc")
        self.assertEqual(second_call_kwargs["headers"]["file_size"], "12345")

        # Step 3: Finish Call
        third_call_args, third_call_kwargs = mock_post.call_args_list[2]
        self.assertIn("video_reels", third_call_args[0])
        self.assertEqual(third_call_kwargs["params"]["upload_phase"], "finish")
        self.assertEqual(third_call_kwargs["params"]["video_id"], "fb_video_789")
        self.assertEqual(third_call_kwargs["params"]["video_state"], "PUBLISHED")
        self.assertEqual(third_call_kwargs["params"]["description"], "Check out OtakKepo! #viral")

    @patch("app.services.facebook.config.facebook", _CONFIG_BASE)
    @patch("app.services.facebook.os.path.exists", return_value=True)
    @patch("app.services.facebook.os.path.getsize", return_value=12345)
    @patch("builtins.open", mock_open(read_data=b"fake_video_bytes"))
    @patch("app.services.facebook.requests.post")
    def test_upload_reel_scheduled_success(self, mock_post, _getsize, _exists):
        mock_post.side_effect = [
            _mock_json_response({"video_id": "fb_video_789", "upload_url": "https://rupload.fb.com/upload"}),
            _mock_json_response({"success": True}),
            _mock_json_response({"success": True, "id": "reel_published_999"})
        ]

        svc = FacebookService()
        result = svc.upload_reel("/fake/path.mp4", "Check out OtakKepo! #viral", publish_at="2026-06-25T12:00:00Z")

        self.assertTrue(result["success"])
        self.assertEqual(result["video_id"], "reel_published_999")
        self.assertEqual(mock_post.call_count, 3)

        # Verify Finish Call arguments for scheduling
        third_call_args, third_call_kwargs = mock_post.call_args_list[2]
        self.assertEqual(third_call_kwargs["params"]["video_state"], "SCHEDULED")
        self.assertEqual(third_call_kwargs["params"]["scheduled_publish_time"], 1782388800)

    @patch("app.services.facebook.config.facebook", {**_CONFIG_BASE, "enabled": False})
    def test_upload_reel_not_enabled(self):
        svc = FacebookService()
        result = svc.upload_reel("/fake/path.mp4", "Test Caption")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Facebook integration not configured")


if __name__ == "__main__":
    unittest.main()
