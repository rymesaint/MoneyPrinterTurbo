import os
import requests
from loguru import logger
from app.config import config


class FacebookService:
    def __init__(self):
        pass

    def is_configured(self) -> bool:
        """
        Check if Facebook integration is enabled and configured correctly.
        """
        enabled = config.facebook.get("enabled", False)
        page_id = config.facebook.get("page_id", "")
        access_token = config.facebook.get("access_token", "")
        return bool(enabled and page_id and access_token)

    def upload_reel(self, video_path: str, caption: str, publish_at: str = None) -> dict:
        """
        Uploads and publishes a video as a Facebook Reel.
        
        Args:
            video_path: Local path to the MP4 file
            caption: Reel description/caption
            publish_at: ISO 8601 string for scheduled publication

        Returns:
            dict: Operation status containing success state and video_id/error details.
        """
        if not self.is_configured():
            logger.warning("Facebook Reels upload skipped: Not configured or enabled.")
            return {"success": False, "error": "Facebook integration not configured"}

        if not os.path.exists(video_path):
            logger.error(f"Facebook Reels upload failed: Video file not found at {video_path}")
            return {"success": False, "error": f"Video file not found: {video_path}"}

        page_id = config.facebook.get("page_id", "")
        access_token = config.facebook.get("access_token", "")
        api_version = config.facebook.get("api_version", "v20.0")

        base_url = f"https://graph.facebook.com/{api_version}/{page_id}"

        try:
            logger.info(f"Initiating Facebook Reels upload session for Page: {page_id}")
            
            # Step 1: Start upload phase
            init_url = f"{base_url}/video_reels"
            params = {
                "upload_phase": "start",
                "access_token": access_token
            }
            res = requests.post(init_url, params=params, timeout=30)
            res.raise_for_status()
            init_data = res.json()
            
            video_id = init_data.get("video_id")
            upload_url = init_data.get("upload_url")
            
            if not video_id or not upload_url:
                logger.error(f"Facebook Reels initialization failed to return video_id/upload_url. Response: {init_data}")
                return {"success": False, "error": f"Failed to initialize upload session: {init_data}"}

            # Step 2: Upload file binary
            file_size = os.path.getsize(video_path)
            logger.info(f"Uploading Reel binary to Facebook ({file_size} bytes)...")
            
            headers = {
                "Authorization": f"OAuth {access_token}",
                "offset": "0",
                "file_size": str(file_size),
                "Content-Type": "application/octet-stream"
            }
            
            with open(video_path, "rb") as f:
                upload_res = requests.post(upload_url, headers=headers, data=f, timeout=300)
                upload_res.raise_for_status()
                
            logger.info(f"Binary upload completed. Facebook Response: {upload_res.text}")

            # Step 3: Finish upload phase
            logger.info("Finishing and publishing Facebook Reel...")
            finish_url = f"{base_url}/video_reels"
            finish_params = {
                "upload_phase": "finish",
                "access_token": access_token,
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": caption
            }

            if publish_at:
                try:
                    from datetime import datetime
                    clean_str = publish_at
                    if clean_str.endswith("Z"):
                        clean_str = clean_str[:-1] + "+00:00"
                    dt = datetime.fromisoformat(clean_str)
                    timestamp = int(dt.timestamp())
                    finish_params["video_state"] = "SCHEDULED"
                    finish_params["scheduled_publish_time"] = timestamp
                    logger.info(f"Scheduling Facebook Reel for: {publish_at} (Timestamp: {timestamp})")
                except Exception as ex:
                    logger.warning(f"Failed to parse publish_at '{publish_at}' for Facebook scheduling: {ex}")

            finish_res = requests.post(finish_url, params=finish_params, timeout=30)
            finish_res.raise_for_status()
            finish_data = finish_res.json()

            if finish_data.get("success") or "id" in finish_data:
                published_id = finish_data.get("id", video_id)
                if finish_params.get("video_state") == "SCHEDULED":
                    logger.info(f"✅ Facebook Reel scheduled successfully! Page ID: {page_id}, Video ID: {published_id}")
                else:
                    logger.info(f"✅ Facebook Reel published successfully! Page ID: {page_id}, Video ID: {published_id}")
                return {"success": True, "video_id": published_id}
            else:
                logger.warning(f"Facebook Reels publish returned unexpected response: {finish_data}")
                return {"success": False, "error": f"Publish finish failure: {finish_data}"}

        except requests.exceptions.RequestException as e:
            err_msg = f"Network/API request failed during Facebook upload: {str(e)}"
            if e.response is not None:
                err_msg += f" - Response: {e.response.text}"
            logger.exception(err_msg)
            return {"success": False, "error": err_msg}
        except Exception as e:
            logger.exception(f"Unexpected error uploading Facebook Reel: {str(e)}")
            return {"success": False, "error": str(e)}


facebook_service = FacebookService()
