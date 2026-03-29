# publishers/facebook_publisher.py
# Handles all Facebook Graph API interactions.
# Requires a Facebook Page and a System User Page Access Token.
# Supports text-only, text + image, and text + video posts.

import requests
from config.settings import FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID

API_BASE = "https://graph.facebook.com/v25.0"

# Supported file types
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def _detect_media_type(filename: str) -> str:
    """Returns 'image', 'video', or 'unknown' based on file extension."""
    import os
    ext = os.path.splitext(filename.lower())[1]
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    return "unknown"


def _upload_video(video_bytes: bytes, title: str = "Video Post") -> dict:
    """
    Uploads a video to Facebook Page using the resumable upload API.
    Returns dict with success, video_id, and error keys.

    Facebook video upload is a two-step process:
    Step 1: Initialize upload session and get upload URL
    Step 2: Upload video bytes to the upload URL
    """
    file_size = len(video_bytes)

    # Step 1: Initialize upload session
    init_response = requests.post(
        f"{API_BASE}/{FACEBOOK_PAGE_ID}/videos",
        data={
            "upload_phase":  "start",
            "file_size":     file_size,
            "access_token":  FACEBOOK_PAGE_ACCESS_TOKEN,
        },
        timeout=15,
    )

    init_data = init_response.json()

    if "upload_session_id" not in init_data:
        return {
            "success":  False,
            "video_id": None,
            "error":    f"Video init failed: {init_data}",
        }

    upload_session_id = init_data["upload_session_id"]
    video_id          = init_data.get("video_id", "")
    start_offset      = int(init_data.get("start_offset", 0))
    end_offset        = int(init_data.get("end_offset", file_size))

    # Step 2: Upload video chunk
    chunk = video_bytes[start_offset:end_offset]

    transfer_response = requests.post(
        f"{API_BASE}/{FACEBOOK_PAGE_ID}/videos",
        data={
            "upload_phase":      "transfer",
            "upload_session_id": upload_session_id,
            "start_offset":      start_offset,
            "access_token":      FACEBOOK_PAGE_ACCESS_TOKEN,
        },
        files={
            "video_file_chunk": ("video.mp4", chunk, "application/octet-stream"),
        },
        timeout=300,
    )

    transfer_data = transfer_response.json()

    if "start_offset" not in transfer_data:
        return {
            "success":  False,
            "video_id": None,
            "error":    f"Video transfer failed: {transfer_data}",
        }

    # Step 3: Finalize upload
    finish_response = requests.post(
        f"{API_BASE}/{FACEBOOK_PAGE_ID}/videos",
        data={
            "upload_phase":      "finish",
            "upload_session_id": upload_session_id,
            "access_token":      FACEBOOK_PAGE_ACCESS_TOKEN,
            "title":             title,
            "published":         "true",
        },
        timeout=30,
    )

    finish_data = finish_response.json()

    if finish_data.get("success"):
        return {
            "success":  True,
            "video_id": video_id,
            "error":    None,
        }
    else:
        return {
            "success":  False,
            "video_id": None,
            "error":    f"Video finalize failed: {finish_data}",
        }


def post_to_facebook(
    text:        str,
    image_bytes: bytes | None = None,
    video_bytes: bytes | None = None,
    filename:    str          = "media.mp4",
) -> dict:
    """
    Posts to a Facebook Page. Supports text-only, text + image, or text + video.
    If both image_bytes and video_bytes are provided, image takes priority.

    Args:
        text:        The post copy.
        image_bytes: Optional raw image bytes (JPG, PNG, GIF, WEBP).
        video_bytes: Optional raw video bytes (MP4, MOV).
        filename:    Original filename -- used to determine media type for display.

    Returns:
        {
            "success": bool,
            "post_id": str or None,
            "error":   str or None,
        }
    """
    if not FACEBOOK_PAGE_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        return {
            "success": False,
            "post_id": None,
            "error":   "Facebook credentials not configured in .env",
        }

    try:
        # Image post
        if image_bytes:
            response = requests.post(
                f"{API_BASE}/{FACEBOOK_PAGE_ID}/photos",
                data={
                    "caption":      text,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
                    "published":    "true",
                },
                files={
                    "source": ("image.jpg", image_bytes, "image/jpeg"),
                },
                timeout=60,
            )

            data = response.json()

            if response.status_code == 200 and "id" in data:
                return {
                    "success": True,
                    "post_id": data["id"],
                    "error":   None,
                }
            else:
                error_msg = data.get("error", {}).get("message", response.text)
                return {
                    "success": False,
                    "post_id": None,
                    "error":   f"HTTP {response.status_code}: {error_msg}",
                }

        # Video post
        elif video_bytes:
            video_result = _upload_video(video_bytes, title=text[:100])

            if not video_result["success"]:
                return {
                    "success": False,
                    "post_id": None,
                    "error":   video_result["error"],
                }

            # Update the video post with the caption text
            video_id = video_result["video_id"]
            update_response = requests.post(
                f"{API_BASE}/{video_id}",
                data={
                    "description":  text,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
                },
                timeout=15,
            )

            return {
                "success": True,
                "post_id": video_id,
                "error":   None,
            }

        # Text-only post
        else:
            response = requests.post(
                f"{API_BASE}/{FACEBOOK_PAGE_ID}/feed",
                json={
                    "message":      text,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
                    "published":    True,
                },
                timeout=15,
            )

            data = response.json()

            if response.status_code == 200 and "id" in data:
                return {
                    "success": True,
                    "post_id": data["id"],
                    "error":   None,
                }
            else:
                error_msg = data.get("error", {}).get("message", response.text)
                return {
                    "success": False,
                    "post_id": None,
                    "error":   f"HTTP {response.status_code}: {error_msg}",
                }

    except Exception as e:
        return {
            "success": False,
            "post_id": None,
            "error":   str(e),
        }