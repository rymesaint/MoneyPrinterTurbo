import os
import random
import threading
import time
from typing import List
from urllib.parse import urlencode

import requests
from loguru import logger
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.config import config
from app.models.schema import MaterialInfo, VideoAspect, VideoConcatMode
from app.utils import utils

# Thread-safe counter for API key rotation
_api_key_counter = 0
_api_key_lock = threading.Lock()


def _get_tls_verify() -> bool:
    # 默认开启 TLS 证书校验，防止素材搜索和下载过程被中间人篡改。
    # 仅在企业代理、自签证书等明确需要的场景下，允许用户通过
    # `config.toml` 显式设置 `tls_verify = false` 临时关闭。
    tls_verify = config.app.get("tls_verify", True)
    if isinstance(tls_verify, str):
        tls_verify = tls_verify.strip().lower() not in ("0", "false", "no", "off")

    if not tls_verify:
        logger.warning(
            "TLS certificate verification is disabled by config.app.tls_verify=false. "
            "Only use this in trusted proxy environments."
        )

    return bool(tls_verify)


def get_api_key(cfg_key: str):
    api_keys = config.app.get(cfg_key)
    if not api_keys:
        raise ValueError(
            f"\n\n##### {cfg_key} is not set #####\n\nPlease set it in the config.toml file: {config.config_file}\n\n"
            f"{utils.to_json(config.app)}"
        )

    # if only one key is provided, return it
    if isinstance(api_keys, str):
        return api_keys

    global _api_key_counter
    with _api_key_lock:
        _api_key_counter += 1
        return api_keys[_api_key_counter % len(api_keys)]


def search_videos_pexels(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    aspect = VideoAspect(video_aspect)
    video_orientation = aspect.name
    video_width, video_height = aspect.to_resolution()
    api_key = get_api_key("pexels_api_keys")
    headers = {
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    # Build URL
    params = {"query": search_term, "per_page": 20, "orientation": video_orientation}
    query_url = f"https://api.pexels.com/videos/search?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url,
            headers=headers,
            proxies=config.proxy,
            verify=_get_tls_verify(),
            timeout=(30, 60),
        )
        response = r.json()
        video_items = []
        if "videos" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items
        videos = response["videos"]
        # loop through each video in the result
        for v in videos:
            duration = v["duration"]
            # check if video has desired minimum duration
            if duration < minimum_duration:
                continue
            video_files = v["video_files"]
            # loop through each url to determine the best quality
            for video in video_files:
                w = int(video["width"])
                h = int(video["height"])
                if w == video_width and h == video_height:
                    item = MaterialInfo()
                    item.provider = "pexels"
                    item.url = video["link"]
                    item.duration = duration
                    video_items.append(item)
                    break
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def search_videos_pixabay(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    aspect = VideoAspect(video_aspect)

    video_width, video_height = aspect.to_resolution()

    api_key = get_api_key("pixabay_api_keys")
    # Build URL
    params = {
        "q": search_term,
        "video_type": "all",  # Accepted values: "all", "film", "animation"
        "per_page": 50,
        "key": api_key,
    }
    query_url = f"https://pixabay.com/api/videos/?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url, proxies=config.proxy, verify=_get_tls_verify(), timeout=(30, 60)
        )
        response = r.json()
        video_items = []
        if "hits" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items
        videos = response["hits"]
        # loop through each video in the result
        for v in videos:
            duration = v["duration"]
            # check if video has desired minimum duration
            if duration < minimum_duration:
                continue
            video_files = v["videos"]
            # loop through each url to determine the best quality
            for video_type in video_files:
                video = video_files[video_type]
                w = int(video["width"])
                # h = int(video["height"])
                if w >= video_width:
                    item = MaterialInfo()
                    item.provider = "pixabay"
                    item.url = video["url"]
                    item.duration = duration
                    video_items.append(item)
                    break
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def search_videos_coverr(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    """
    Coverr (https://coverr.co) - free HD/4K stock videos,
    subject to Coverr license terms (https://coverr.co/license).

    Coverr API notes (based on official docs at api.coverr.co/docs/):
      - 鉴权: Authorization: Bearer <api_key>
      - 搜索端点: GET /videos?query=...,响应结构 {"hits": [...], ...}
      - 加 ?urls=true 在搜索响应里直接返回 mp4 直链
      - URL 是 signed JWT(绑定 API key,无过期时间)
      - Coverr 库以 16:9 横屏为主,9:16 portrait 占比极低(约 1%)
        因此本函数不做 aspect_ratio 过滤,由下游 video.py 的
        resize + letterbox 逻辑统一处理
      - duration 字段同时存在 number 和 string 两种形态,本函数都接受

    本函数使用 urls.mp4_download 字段作为下载地址 —— 按 Coverr 官方文档
    (https://api.coverr.co/docs/videos/#download-a-video) 的说法,
    GET 这个 URL 本身就被 Coverr 当作一次合法的 download 事件计入统计,
    无需再调用 PATCH /videos/:id/stats/downloads。
    """
    api_key = get_api_key("coverr_api_keys")
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "query": search_term,
        "page_size": 20,
        "urls": "true",
        "sort": "popular",
    }
    query_url = f"https://api.coverr.co/videos?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url,
            headers=headers,
            proxies=config.proxy,
            verify=_get_tls_verify(),
            timeout=(30, 60),
        )
        response = r.json()
        video_items: List[MaterialInfo] = []

        if not isinstance(response, dict) or "hits" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items

        for v in response["hits"]:
            # duration 在不同响应里可能是 number(11.625) 或 string("10.500000")
            try:
                duration = int(float(v.get("duration") or 0))
            except (TypeError, ValueError):
                continue
            if duration < minimum_duration:
                continue

            video_id = v.get("id")
            mp4_download_url = (v.get("urls") or {}).get("mp4_download")
            if not video_id or not mp4_download_url:
                continue

            item = MaterialInfo()
            item.provider = "coverr"
            item.url = mp4_download_url
            item.duration = duration
            video_items.append(item)
        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def search_videos_vecteezy(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    """
    Vecteezy (https://www.vecteezy.com) - stock video library,
    subject to Vecteezy license terms (https://www.vecteezy.com/licensing).

    API v2 docs: https://www.vecteezy.com/api-docs/index.html
    - Search: GET /v2/{account_id}/resources?term=...&content_type=videos
    - Download: GET /v2/{account_id}/resources/{id}/download -> {url: "..."}
    - Auth: Bearer token

    Vecteezy search doesn't return direct download URLs, so we
    call the download endpoint per matched resource to resolve.

    Config requires:
      vecteezy_account_id = "<your_account_id>"
      vecteezy_api_keys = ["<your_api_key>"]
    """
    aspect = VideoAspect(video_aspect)
    video_width, video_height = aspect.to_resolution()

    api_key = get_api_key("vecteezy_api_keys")
    account_id = config.app.get("vecteezy_account_id", "")
    if not account_id:
        logger.error("vecteezy_account_id not set in config.toml [app] section")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    params = {
        "term": search_term,
        "content_type": "videos",
        "page": 1,
        "per_page": 20,
        "duration": f"{minimum_duration}_99999",
        "sort_by": "relevant",
    }
    query_url = f"https://api.vecteezy.com/v2/{account_id}/resources?{urlencode(params)}"
    logger.info(f"searching videos: {query_url}, with proxies: {config.proxy}")

    try:
        r = requests.get(
            query_url,
            headers=headers,
            proxies=config.proxy,
            verify=_get_tls_verify(),
            timeout=(30, 60),
        )
        response = r.json()
        video_items = []

        if "resources" not in response:
            logger.error(f"search videos failed: {response}")
            return video_items

        for resource in response["resources"]:
            resource_id = resource.get("id")
            if not resource_id:
                continue

            sizes = resource.get("available_download_sizes") or []
            matched_size = None
            for sz in sizes:
                if (
                    int(sz.get("width", 0)) == video_width
                    and int(sz.get("height", 0)) == video_height
                ):
                    matched_size = sz.get("id", "")
                    break

            if not matched_size:
                continue

            try:
                dl_resp = requests.get(
                    f"https://api.vecteezy.com/v2/{account_id}/resources/{resource_id}/download",
                    headers=headers,
                    proxies=config.proxy,
                    verify=_get_tls_verify(),
                    timeout=(30, 60),
                )
                dl_data = dl_resp.json()
                video_url = dl_data.get("url")
                if not video_url:
                    continue

                item = MaterialInfo()
                item.provider = "vecteezy"
                item.url = video_url
                item.duration = minimum_duration
                video_items.append(item)
            except Exception as e:
                logger.warning(
                    f"failed to get download URL for Vecteezy resource "
                    f"{resource_id}: {str(e)}"
                )
                continue

        return video_items
    except Exception as e:
        logger.error(f"search videos failed: {str(e)}")

    return []


def save_video(video_url: str, save_dir: str = "") -> str:
    if not save_dir:
        save_dir = utils.storage_dir("cache_videos")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    url_without_query = video_url.split("?")[0]
    url_hash = utils.md5(url_without_query)
    video_id = f"vid-{url_hash}"
    video_path = f"{save_dir}/{video_id}.mp4"

    # if video already exists, return the path
    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        logger.info(f"video already exists: {video_path}")
        return video_path

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # if video does not exist, download it
    with open(video_path, "wb") as f:
        f.write(
            requests.get(
                video_url,
                headers=headers,
                proxies=config.proxy,
                verify=_get_tls_verify(),
                timeout=(60, 240),
            ).content
        )

    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        clip = None
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            fps = clip.fps
            if duration > 0 and fps > 0:
                return video_path
        except Exception as e:
            logger.warning(f"invalid video file: {video_path} => {str(e)}")
            try:
                os.remove(video_path)
            except Exception as remove_error:
                logger.warning(
                    f"failed to remove invalid video file: {video_path}, error: {str(remove_error)}"
                )
        finally:
            if clip is not None:
                try:
                    clip.close()
                except Exception as close_error:
                    logger.warning(
                        f"failed to close video clip: {video_path}, error: {str(close_error)}"
                    )
    return ""


def search_videos_kling(
    search_term: str,
    minimum_duration: int,
    video_aspect: VideoAspect = VideoAspect.portrait,
) -> List[MaterialInfo]:
    api_key = config.app.get("kling_api_key")
    if not api_key:
        logger.warning("kling_api_key not configured, falling back to pexels")
        return search_videos_pexels(search_term, minimum_duration, video_aspect)

    aspect = VideoAspect(video_aspect)
    ratio = aspect.value

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    duration = "5"
    if minimum_duration > 5:
        duration = "10"

    model_name = config.app.get("kling_model_name", "kling-v1")

    data = {
        "prompt": search_term,
        "ratio": ratio,
        "duration": duration,
        "model_name": model_name
    }

    try:
        r = requests.post(
            "https://api.klingai.com/v1/videos/text2video",
            headers=headers,
            json=data,
            proxies=config.proxy,
            verify=_get_tls_verify(),
            timeout=(30, 60)
        )
        res = r.json()
        if res.get("code") != 0:
            logger.error(f"Kling video generation submit failed: {res.get('message')}. Falling back to pexels.")
            return search_videos_pexels(search_term, minimum_duration, video_aspect)
        
        task_id = res.get("data", {}).get("task_id")
        if not task_id:
            logger.error("Kling API response did not contain task_id. Falling back to pexels.")
            return search_videos_pexels(search_term, minimum_duration, video_aspect)

        logger.info(f"Kling video generation task submitted: {task_id}")

        import time
        max_retries = 60
        poll_interval = 5
        video_url = None
        for i in range(max_retries):
            time.sleep(poll_interval)
            status_resp = requests.get(
                f"https://api.klingai.com/v1/videos/text2video/{task_id}",
                headers=headers,
                proxies=config.proxy,
                verify=_get_tls_verify(),
                timeout=(30, 60)
            )
            status_data = status_resp.json()
            if status_data.get("code") != 0:
                logger.error(f"Kling polling error: {status_data.get('message')}")
                break
            
            task_info = status_data.get("data", {})
            status = task_info.get("task_status")
            logger.info(f"Kling task {task_id} status: {status}")
            if status == "SUCCESS":
                videos = task_info.get("video_result", {}).get("videos", [])
                if videos:
                    video_url = videos[0].get("url")
                break
            elif status in ["FAILED", "CANCELLED"]:
                logger.error(f"Kling generation task failed: {task_info.get('task_status_msg')}")
                break

        if video_url:
            item = MaterialInfo()
            item.provider = "kling"
            item.url = video_url
            item.duration = int(duration)
            return [item]

        logger.warning(f"Kling generation failed or timed out for task {task_id}. Falling back to pexels.")
    except Exception as e:
        logger.error(f"Kling generation error: {str(e)}. Falling back to pexels.")

    return search_videos_pexels(search_term, minimum_duration, video_aspect)


def download_videos(
    task_id: str,
    search_terms: List[str],
    source: str = "pexels",
    video_aspect: VideoAspect = VideoAspect.portrait,
    video_concat_mode: VideoConcatMode = VideoConcatMode.random,
    audio_duration: float = 0.0,
    max_clip_duration: int = 5,
    match_script_order: bool = False,
) -> List[str]:
    search_videos = search_videos_pexels
    if source == "pixabay":
        search_videos = search_videos_pixabay
    elif source == "coverr":
        search_videos = search_videos_coverr
    elif source == "vecteezy":
        search_videos = search_videos_vecteezy
    elif source == "kling":
        search_videos = search_videos_kling

    material_directory = config.app.get("material_directory", "").strip()
    if material_directory == "task":
        material_directory = utils.task_dir(task_id)
    elif material_directory and not os.path.isdir(material_directory):
        material_directory = ""

    if match_script_order:
        return _download_videos_by_script_order(
            task_id=task_id,
            search_terms=search_terms,
            search_videos=search_videos,
            video_aspect=video_aspect,
            audio_duration=audio_duration,
            max_clip_duration=max_clip_duration,
            material_directory=material_directory,
        )

    valid_video_items = []
    valid_video_urls = []
    found_duration = 0.0
    for search_term in search_terms:
        video_items = search_videos(
            search_term=search_term,
            minimum_duration=max_clip_duration,
            video_aspect=video_aspect,
        )
        logger.info(f"found {len(video_items)} videos for '{search_term}'")

        for item in video_items:
            if item.url not in valid_video_urls:
                valid_video_items.append(item)
                valid_video_urls.append(item.url)
                found_duration += item.duration

    logger.info(
        f"found total videos: {len(valid_video_items)}, required duration: {audio_duration} seconds, found duration: {found_duration} seconds"
    )
    video_paths = []

    concat_mode_value = getattr(video_concat_mode, "value", video_concat_mode)
    if concat_mode_value == VideoConcatMode.random.value:
        random.shuffle(valid_video_items)

    total_duration = 0.0
    for item in valid_video_items:
        try:
            logger.info(f"downloading video: {item.url}")
            saved_video_path = save_video(
                video_url=item.url, save_dir=material_directory
            )
            if saved_video_path:
                logger.info(f"video saved: {saved_video_path}")
                video_paths.append(saved_video_path)
                seconds = min(max_clip_duration, item.duration)
                total_duration += seconds
                if total_duration > audio_duration:
                    logger.info(
                        f"total duration of downloaded videos: {total_duration} seconds, skip downloading more"
                    )
                    break
        except Exception as e:
            logger.error(f"failed to download video: {utils.to_json(item)} => {str(e)}")
    logger.success(f"downloaded {len(video_paths)} videos")
    return video_paths


def _download_videos_by_script_order(
    task_id: str,
    search_terms: List[str],
    search_videos,
    video_aspect: VideoAspect,
    audio_duration: float,
    max_clip_duration: int,
    material_directory: str,
) -> List[str]:
    """
    按脚本文案顺序下载素材。

    默认下载逻辑会把所有关键词的候选素材合并成一个大列表；如果第一个
    关键词返回很多结果，最终下载时可能一直消耗这个关键词的素材，后续
    脚本主题就排不上时间线。这里按关键词分组后轮询下载：
    第 1 轮取每个关键词的第 1 个候选，第 2 轮取每个关键词的第 2 个候选。
    这样在不重写视频合成引擎的前提下，尽量保证素材顺序贴近文案顺序。
    """
    logger.info("downloading videos with script-order material matching")
    candidate_groups = []
    valid_video_urls = set()
    found_duration = 0.0

    for search_term in search_terms:
        video_items = search_videos(
            search_term=search_term,
            minimum_duration=max_clip_duration,
            video_aspect=video_aspect,
        )
        logger.info(f"found {len(video_items)} videos for '{search_term}'")

        term_items = []
        for item in video_items:
            if item.url in valid_video_urls:
                continue
            term_items.append(item)
            valid_video_urls.add(item.url)
            found_duration += item.duration

        if term_items:
            candidate_groups.append((search_term, term_items))

    logger.info(
        f"found total ordered video candidates: {sum(len(items) for _, items in candidate_groups)}, "
        f"required duration: {audio_duration} seconds, found duration: {found_duration} seconds"
    )

    video_paths = []
    total_duration = 0.0
    candidate_index = 0
    while candidate_groups and total_duration <= audio_duration:
        has_candidate = False
        for search_term, term_items in candidate_groups:
            if candidate_index >= len(term_items):
                continue

            has_candidate = True
            item = term_items[candidate_index]
            try:
                logger.info(
                    f"downloading ordered video for '{search_term}': {item.url}"
                )
                saved_video_path = save_video(
                    video_url=item.url, save_dir=material_directory
                )
                if saved_video_path:
                    logger.info(f"video saved: {saved_video_path}")
                    video_paths.append(saved_video_path)
                    total_duration += min(max_clip_duration, item.duration)
                    if total_duration > audio_duration:
                        logger.info(
                            f"total duration of downloaded videos: {total_duration} seconds, skip downloading more"
                        )
                        break
            except Exception as e:
                logger.error(
                    f"failed to download ordered video: {utils.to_json(item)} => {str(e)}"
                )

        if not has_candidate:
            break
        candidate_index += 1

    logger.success(f"downloaded {len(video_paths)} ordered videos")
    return video_paths


def download_ccmixter_bgm(keyword: str, save_dir: str = "") -> str:
    """
    Search ccMixter API for keyword and download the first matching track to save_dir.
    Returns the filename of the downloaded MP3 file (relative to utils.song_dir() or absolute if custom save_dir), or "" if failed.
    """
    if not keyword:
        return ""

    if not save_dir:
        save_dir = utils.song_dir()

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    keyword_clean = "".join(c for c in keyword if c.isalnum() or c.isspace()).strip()
    if not keyword_clean:
        keyword_clean = "ambient"

    url = "http://ccmixter.org/api/query"
    params = {
        "f": "json",
        "search": keyword_clean,
        "limit": 5
    }

    logger.info(f"searching ccMixter BGM with keyword: '{keyword_clean}'")
    try:
        r = requests.get(url, params=params, proxies=config.proxy, timeout=30)
        if r.status_code != 200:
            logger.error(f"ccMixter API returned status code {r.status_code}")
            return ""

        data = r.json()
        if not data or not isinstance(data, list):
            logger.warning("No music files found on ccMixter.")
            return ""

        for track in data:
            files = track.get("files")
            if not files or not isinstance(files, list):
                continue

            for file_info in files:
                download_url = file_info.get("download_url")
                file_name = file_info.get("file_name")
                if download_url and file_name:
                    # Clean filename to prevent path traversal
                    safe_name = "".join(c for c in file_name if c.isalnum() or c in "._-").strip()
                    save_path = os.path.join(save_dir, f"ccmixter-{safe_name}")

                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        logger.info(f"ccMixter BGM already exists: {save_path}")
                        return f"ccmixter-{safe_name}"

                    logger.info(f"downloading ccMixter BGM: {download_url}")
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                        "Referer": "http://ccmixter.org/"
                    }
                    r_dl = requests.get(download_url, headers=headers, proxies=config.proxy, timeout=120)
                    if r_dl.status_code != 200 or len(r_dl.content) < 10000:
                        logger.warning(f"Failed to download valid BGM from ccMixter, status: {r_dl.status_code}, length: {len(r_dl.content) if r_dl else 0}")
                        continue

                    with open(save_path, "wb") as f:
                        f.write(r_dl.content)

                    if os.path.exists(save_path) and os.path.getsize(save_path) > 10000:
                        logger.success(f"ccMixter BGM saved to: {save_path}")
                        return f"ccmixter-{safe_name}"
    except Exception as e:
        logger.error(f"Failed to query or download from ccMixter: {str(e)}")

    return ""


if __name__ == "__main__":
    download_videos(
        "test123", ["Money Exchange Medium"], audio_duration=100, source="pixabay"
    )

