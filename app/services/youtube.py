import os
import json
from datetime import datetime, timezone
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from loguru import logger
from app.config import config

class YouTubeService:
    def __init__(self):
        # Read parameters on initial load
        self.scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ]
        self.credentials = None

    def is_configured(self) -> bool:
        # Check enabled state from config
        enabled = config.youtube.get("enabled", False)
        client_secrets_file = config.youtube.get("client_secrets_file", "youtube_client_secrets.json")
        return bool(enabled and os.path.exists(client_secrets_file))

    def load_credentials(self):
        credentials_file = config.youtube.get("credentials_file", "youtube_credentials.json")
        if os.path.exists(credentials_file):
            try:
                self.credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(
                    credentials_file, self.scopes
                )
                logger.info("Loaded existing YouTube credentials.")
            except Exception as e:
                logger.error(f"Failed to load YouTube credentials: {e}")
                self.credentials = None

    def get_authenticated_service(self):
        client_secrets_file = config.youtube.get("client_secrets_file", "youtube_client_secrets.json")
        credentials_file = config.youtube.get("credentials_file", "youtube_credentials.json")

        if not self.credentials:
            self.load_credentials()

        # Force refresh if scopes in json don't match self.scopes
        needs_refresh = False
        if os.path.exists(credentials_file):
            try:
                import json
                with open(credentials_file, "r") as f:
                    data = json.load(f)
                file_scopes = data.get("scopes", [])
                if any(s not in file_scopes for s in self.scopes):
                    needs_refresh = True
            except Exception:
                pass

        if self.credentials and (self.credentials.expired or needs_refresh) and self.credentials.refresh_token:
            try:
                from google.auth.transport.requests import Request
                self.credentials.refresh(Request())
                with open(credentials_file, "w") as f:
                    f.write(self.credentials.to_json())
                logger.info("Refreshed YouTube credentials (expired or updated scopes).")
            except Exception as e:
                logger.error(f"Failed to refresh YouTube credentials: {e}")
                self.credentials = None

        if not self.credentials:
            logger.warning("YouTube credentials not found or invalid. Initiating OAuth flow.")
            if not os.path.exists(client_secrets_file):
                logger.error(f"Client secrets file not found: {client_secrets_file}")
                return None
            
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, self.scopes
            )
            
            # Detect headless environment (Docker / remote server)
            from app.config.config import is_running_in_container
            in_container = is_running_in_container()
            is_headless = in_container or os.environ.get("HEADLESS", "").lower() == "true"
            if os.name == "posix" and not os.environ.get("DISPLAY"):
                is_headless = True
                
            open_browser = not is_headless
            oauth_port = config.youtube.get("oauth_port", 0)
            oauth_host = config.youtube.get("oauth_host", "localhost")
            
            if is_headless:
                logger.warning(
                    "\n========================================================================\n"
                    "⚠️ HEADLESS ENVIRONMENT DETECTED (Docker or Remote Server)\n"
                    "Automatic browser opening disabled. Copy the URL below, authorize in your\n"
                    "local browser, and the credentials will be generated automatically.\n"
                    "========================================================================\n"
                )
                
            try:
                self.credentials = flow.run_local_server(
                    host=oauth_host,
                    port=oauth_port,
                    open_browser=open_browser,
                    authorization_prompt_message="Please visit this URL to authorize the app:\n{url}"
                )
            except Exception as e:
                logger.error(
                    f"OAuth flow failed: {e}\n"
                    "Make sure your credentials file is valid, or run MPT locally first "
                    "to generate 'youtube_credentials.json' and upload it to the server."
                )
                return None
            
            # Save the credentials for next run
            with open(credentials_file, "w") as f:
                f.write(self.credentials.to_json())
            logger.info(f"YouTube credentials saved to {credentials_file}")

        return build("youtube", "v3", credentials=self.credentials)

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        privacy_status: str = "public",
        category_id: str = "22",
        tags: list = None,
        publish_at: str = None,
        progress_callback = None
    ) -> dict:
        if not self.is_configured():
            logger.warning("YouTube integration is not configured or enabled.")
            return {"success": False, "error": "YouTube upload not configured"}

        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found: {video_path}"}

        try:
            youtube = self.get_authenticated_service()
            if not youtube:
                return {"success": False, "error": "Authentication failed"}

            logger.info(f"Uploading {video_path} to YouTube Shorts...")

            # Clean and prepare tags
            video_tags = tags or config.youtube.get("tags", ["shorts", "viral", "mpt"])
            if isinstance(video_tags, str):
                video_tags = [t.strip() for t in video_tags.split(",") if t.strip()]

            # Build metadata body
            body = {
                "snippet": {
                    "title": title[:100],  # Title is capped at 100 chars
                    "description": description[:5000],  # Description is capped at 5000 chars
                    "tags": video_tags,
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": "private" if publish_at else privacy_status,
                    "selfDeclaredMadeForKids": False,
                    "containsSyntheticMedia": config.youtube.get("contains_synthetic_media", True)
                }
            }

            if publish_at:
                body["status"]["publishAt"] = publish_at

            # Chunk size: 1MB. Must be multiple of 256KB
            media = MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    percent = int(status.progress() * 100)
                    logger.info(f"YouTube Upload Progress: {percent}%")
                    if progress_callback:
                        try:
                            progress_callback(percent)
                        except Exception:
                            pass

            video_id = response.get("id")
            logger.info(f"✅ YouTube video uploaded successfully! Video ID: {video_id}")
            return {"success": True, "video_id": video_id}

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return {"success": False, "error": f"YouTube API Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to upload video to YouTube: {e}")
            return {"success": False, "error": str(e)}

    def add_comment(
        self,
        video_id: str,
        comment_text: str,
    ) -> dict:
        """Post a top-level comment on a video and return its id."""
        if not self.is_configured():
            return {"success": False, "error": "YouTube not configured"}
        try:
            youtube = self.get_authenticated_service()
            if not youtube:
                return {"success": False, "error": "Authentication failed"}

            body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text,
                        }
                    },
                }
            }
            res = youtube.commentThreads().insert(
                part="snippet", body=body
            ).execute()
            comment_id = res.get("id")
            logger.info(f"✅ Comment posted on video {video_id}: {comment_id}")
            return {"success": True, "comment_id": comment_id}
        except HttpError as e:
            logger.error(f"YouTube comment API error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            return {"success": False, "error": str(e)}

    def handle_api_error(self, e: Exception) -> dict:
        error_msg = str(e)
        if isinstance(e, HttpError) and e.resp.status == 403:
            error_msg = "Insufficient API scopes or permission error. Please verify your YouTube API access."
        return {"success": False, "error": error_msg}

    def get_channel_info(self) -> dict:
        if not self.is_configured():
            return {"success": False, "error": "YouTube integration is not configured"}
        try:
            youtube = self.get_authenticated_service()
            if not youtube:
                return {"success": False, "error": "Authentication failed"}
            
            try:
                res = youtube.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()
                if res.get("items"):
                    item = res["items"][0]
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    content_details = item.get("contentDetails", {})
                    uploads_playlist = content_details.get("relatedPlaylists", {}).get("uploads")
                    return {
                        "success": True,
                        "title": snippet.get("title"),
                        "customUrl": snippet.get("customUrl"),
                        "thumbnails": snippet.get("thumbnails", {}),
                        "viewCount": stats.get("viewCount", "0"),
                        "subscriberCount": stats.get("subscriberCount", "0"),
                        "videoCount": stats.get("videoCount", "0"),
                        "uploads_playlist": uploads_playlist
                    }
            except Exception as e:
                if hasattr(e, "resp") and e.resp.status == 403:
                    logger.warning("Insufficient scope for channels API. Using fallback profile details.")
                    return {
                        "success": True,
                        "title": "My YouTube Channel",
                        "customUrl": "",
                        "thumbnails": {},
                        "viewCount": "N/A",
                        "subscriberCount": "N/A",
                        "videoCount": "N/A",
                        "uploads_playlist": None
                    }
                raise e
            return {"success": False, "error": "No channel found"}
        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return self.handle_api_error(e)

    def get_my_videos(self, max_results=10) -> dict:
        if not self.is_configured():
            return {"success": False, "error": "YouTube integration is not configured"}
        try:
            youtube = self.get_authenticated_service()
            if not youtube:
                return {"success": False, "error": "Authentication failed"}
            
            video_ids = []
            use_history_fallback = False
            
            try:
                # 1. Get channel uploads playlist
                channel_res = youtube.channels().list(part="contentDetails", mine=True).execute()
                if channel_res.get("items"):
                    uploads_playlist = channel_res["items"][0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
                    if uploads_playlist:
                        # 2. Get playlist items
                        playlist_res = youtube.playlistItems().list(
                            part="snippet,contentDetails",
                            playlistId=uploads_playlist,
                            maxResults=max_results
                        ).execute()
                        video_items = playlist_res.get("items", [])
                        video_ids = [item.get("contentDetails", {}).get("videoId") for item in video_items if item.get("contentDetails", {}).get("videoId")]
            except Exception as e:
                if hasattr(e, "resp") and e.resp.status == 403:
                    logger.warning("Insufficient scope for uploads playlist. Falling back to local task history.")
                    use_history_fallback = True
                else:
                    raise e

            if use_history_fallback or not video_ids:
                from app.services.state import state as task_state
                try:
                    tasks, _ = task_state.get_all_tasks(page=1, page_size=100)
                    for task in tasks:
                        yt_res = task.get("youtube_results")
                        if yt_res and isinstance(yt_res, list):
                            for res in yt_res:
                                if isinstance(res, dict) and res.get("success") and res.get("video_id"):
                                    video_ids.append(res.get("video_id"))
                    # De-duplicate while preserving order
                    seen = set()
                    video_ids = [x for x in video_ids if not (x in seen or seen.add(x))][:max_results]
                except Exception as task_err:
                    logger.error(f"Failed to fetch uploaded video IDs from task history: {task_err}")
            
            if not video_ids:
                return {"success": True, "videos": []}
            
            # 3. Get video statistics & status
            video_res = youtube.videos().list(
                part="snippet,statistics,status",
                id=",".join(video_ids)
            ).execute()
            
            videos = []
            for item in video_res.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                status = item.get("status", {})
                videos.append({
                    "id": item.get("id"),
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "publishedAt": snippet.get("publishedAt"),
                    "thumbnails": snippet.get("thumbnails"),
                    "viewCount": stats.get("viewCount", "0"),
                    "likeCount": stats.get("likeCount", "0"),
                    "commentCount": stats.get("commentCount", "0"),
                    "privacyStatus": status.get("privacyStatus"),
                    "publishAt": status.get("publishAt"),
                    "uploadStatus": status.get("uploadStatus"),
                })
            return {"success": True, "videos": videos}
        except Exception as e:
            logger.error(f"Failed to get channel videos: {e}")
            return self.handle_api_error(e)

    def get_video_stats(self, video_id: str) -> dict:
        if not self.is_configured():
            return {"success": False, "error": "YouTube integration is not configured"}
        try:
            youtube = self.get_authenticated_service()
            if not youtube:
                return {"success": False, "error": "Authentication failed"}
            res = youtube.videos().list(part="snippet,statistics,status", id=video_id).execute()
            if not res.get("items"):
                return {"success": False, "error": "Video not found"}
            item = res["items"][0]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            status = item.get("status", {})
            return {
                "success": True,
                "video": {
                    "id": item.get("id"),
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "publishedAt": snippet.get("publishedAt"),
                    "thumbnails": snippet.get("thumbnails"),
                    "channelTitle": snippet.get("channelTitle"),
                    "viewCount": stats.get("viewCount", "0"),
                    "likeCount": stats.get("likeCount", "0"),
                    "commentCount": stats.get("commentCount", "0"),
                    "privacyStatus": status.get("privacyStatus"),
                    "publishAt": status.get("publishAt"),
                    "uploadStatus": status.get("uploadStatus"),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get video stats: {e}")
            return self.handle_api_error(e)

    def get_trending_videos(self, region_code="US", max_results=10) -> dict:
        if not self.is_configured():
            return {"success": False, "error": "YouTube integration is not configured"}
        try:
            youtube = self.get_authenticated_service()
            if not youtube:
                return {"success": False, "error": "Authentication failed"}
            res = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results
            ).execute()
            videos = []
            for item in res.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                videos.append({
                    "id": item.get("id"),
                    "title": snippet.get("title"),
                    "channelTitle": snippet.get("channelTitle"),
                    "publishedAt": snippet.get("publishedAt"),
                    "thumbnails": snippet.get("thumbnails"),
                    "viewCount": stats.get("viewCount", "0"),
                    "likeCount": stats.get("likeCount", "0"),
                    "commentCount": stats.get("commentCount", "0"),
                })
            return {"success": True, "videos": videos}
        except Exception as e:
            logger.error(f"Failed to get trending videos: {e}")
            return self.handle_api_error(e)

youtube_service = YouTubeService()


def queue_pending_comment(video_id: str, comment_text: str, publish_at: str):
    """Save comment to queue to be posted when video becomes public."""
    queue_file = os.path.join("storage", "pending_youtube_comments.json")
    os.makedirs("storage", exist_ok=True)
    
    # Load existing queue
    queue = []
    if os.path.exists(queue_file):
        try:
            with open(queue_file, "r", encoding="utf-8") as f:
                queue = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read pending comments: {e}")
            
    # Add new entry
    queue.append({
        "video_id": video_id,
        "comment_text": comment_text,
        "publish_at": publish_at,
        "queued_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Save queue
    try:
        with open(queue_file, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=4)
        logger.info(f"Queued comment for scheduled video {video_id}")
    except Exception as e:
        logger.error(f"Failed to save pending comments queue: {e}")


def process_pending_comments():
    """Check all pending comments and post if the video is now public."""
    queue_file = os.path.join("storage", "pending_youtube_comments.json")
    if not os.path.exists(queue_file):
        return
        
    try:
        with open(queue_file, "r", encoding="utf-8") as f:
            queue = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read pending comments: {e}")
        return
        
    if not queue:
        return
        
    logger.info(f"Checking {len(queue)} pending YouTube comments...")
    
    remaining = []
    updated = False
    
    for item in queue:
        video_id = item.get("video_id")
        comment_text = item.get("comment_text")
        
        # Check video status via youtube_service
        try:
            status_res = youtube_service.get_video_stats(video_id)
            if not status_res.get("success"):
                err_msg = status_res.get("error", "")
                if "not found" in err_msg.lower():
                    logger.warning(f"Video {video_id} not found on YouTube. Removing from comment queue.")
                    updated = True
                    continue
                remaining.append(item)
                continue
                
            video_data = status_res.get("video", {})
            privacy = video_data.get("privacyStatus")
            upload_status = video_data.get("uploadStatus")
            
            # If the video is now public/unlisted and processed, post the comment
            if privacy in ["public", "unlisted"] and upload_status == "processed":
                logger.info(f"Video {video_id} is now {privacy}! Posting queued comment...")
                post_res = youtube_service.add_comment(video_id, comment_text)
                if post_res.get("success"):
                    updated = True
                    continue
                else:
                    logger.warning(f"Failed to post queued comment for {video_id}: {post_res.get('error')}")
                    remaining.append(item)
            else:
                remaining.append(item)
        except Exception as e:
            logger.error(f"Error checking status for video {video_id}: {e}")
            remaining.append(item)
            
    if updated:
        try:
            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump(remaining, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to update pending comments queue: {e}")

