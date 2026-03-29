# publishers/linkedin_publisher.py
# Handles all LinkedIn API interactions.
# Supports text-only, text + image, and text + video posts.
# Video upload uses LinkedIn's three-step chunked upload process.

import os
import requests
from config.settings import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN

API_BASE = "https://api.linkedin.com/v2"

HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type":  "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}

# Supported file types
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def _detect_media_type(filename: str) -> str:
    """Returns 'image', 'video', or 'unknown' based on file extension."""
    ext = os.path.splitext(filename.lower())[1]
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    return "unknown"


def _upload_image(image_bytes: bytes) -> str | None:
    """
    Uploads an image to LinkedIn using the two-step register + PUT process.
    Returns the asset URN or None on failure.
    """
    # Step 1: Register upload
    register_payload = {
        "registerUploadRequest": {
            "owner": LINKEDIN_PERSON_URN,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [
                {
                    "identifier":     "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER",
                }
            ],
        }
    }

    register_response = requests.post(
        f"{API_BASE}/assets?action=registerUpload",
        headers=HEADERS,
        json=register_payload,
        timeout=15,
    )

    if register_response.status_code != 200:
        return None

    data       = register_response.json()
    upload_url = data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset_urn  = data["value"]["asset"]

    # Step 2: PUT image bytes to upload URL
    upload_response = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"},
        data=image_bytes,
        timeout=60,
    )

    if upload_response.status_code not in (200, 201):
        return None

    return asset_urn


def _upload_video(video_bytes: bytes, filename: str = "video.mp4") -> str | None:
    """
    Uploads a video to LinkedIn using the three-step process:
    Step 1: Initialize upload and get upload URL + video URN
    Step 2: PUT video bytes to the upload URL
    Step 3: Finalize the upload
    Returns the video URN or None on failure.
    """
    file_size = len(video_bytes)

    # Step 1: Initialize upload
    init_payload = {
        "initializeUploadRequest": {
            "owner":    LINKEDIN_PERSON_URN,
            "fileSizeBytes": file_size,
            "uploadCaptions": False,
            "uploadThumbnail": False,
        }
    }

    init_response = requests.post(
        "https://api.linkedin.com/rest/videos?action=initializeUpload",
        headers={
            "Authorization":             f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type":              "application/json",
            "LinkedIn-Version":          "202406",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json=init_payload,
        timeout=15,
    )

    if init_response.status_code != 200:
        return None

    init_data    = init_response.json()
    value        = init_data.get("value", {})
    upload_url   = value.get("uploadInstructions", [{}])[0].get("uploadUrl", "")
    video_urn    = value.get("video", "")
    upload_token = value.get("uploadToken", "")

    if not upload_url or not video_urn:
        return None

    # Step 2: PUT video bytes to upload URL
    upload_response = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type":  "application/octet-stream",
        },
        data=video_bytes,
        timeout=300,
    )

    if upload_response.status_code not in (200, 201):
        return None

    etag = upload_response.headers.get("ETag", "").strip('"')

    # Step 3: Finalize upload
    finalize_payload = {
        "finalizeUploadRequest": {
            "video":       video_urn,
            "uploadToken": upload_token,
            "uploadedPartIds": [etag] if etag else [],
        }
    }

    finalize_response = requests.post(
        "https://api.linkedin.com/rest/videos?action=finalizeUpload",
        headers={
            "Authorization":             f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type":              "application/json",
            "LinkedIn-Version":          "202406",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json=finalize_payload,
        timeout=30,
    )

    if finalize_response.status_code not in (200, 201):
        return None

    return video_urn


def post_to_linkedin(
    text:        str,
    image_bytes: bytes | None = None,
    video_bytes: bytes | None = None,
    filename:    str          = "media.mp4",
) -> dict:
    """
    Posts to LinkedIn. Supports text-only, text + image, or text + video.
    If both image_bytes and video_bytes are provided, image takes priority.

    Args:
        text:        Post copy, max 1000 characters.
        image_bytes: Optional raw image bytes (JPG, PNG, GIF, WEBP).
        video_bytes: Optional raw video bytes (MP4, MOV).
        filename:    Original filename -- used to determine media type.

    Returns:
        {
            "success": bool,
            "post_id": str or None,
            "error":   str or None,
        }
    """
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        return {
            "success": False,
            "post_id": None,
            "error":   "LinkedIn credentials not configured in .env",
        }

    try:
        # Base post payload
        payload = {
            "author":         LINKEDIN_PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary":   {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        # Attach image if provided
        if image_bytes:
            asset_urn = _upload_image(image_bytes)
            if asset_urn:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "shareMediaCategory"] = "IMAGE"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "media"] = [{"status": "READY", "media": asset_urn}]

        # Attach video if provided and no image
        elif video_bytes:
            video_urn = _upload_video(video_bytes, filename)
            if video_urn:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "shareMediaCategory"] = "VIDEO"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "media"] = [{"status": "READY", "media": video_urn}]

        # Post
        response = requests.post(
            f"{API_BASE}/ugcPosts",
            headers=HEADERS,
            json=payload,
            timeout=30,
        )

        if response.status_code == 201:
            post_id = response.headers.get("x-restli-id", "unknown")
            return {"success": True,  "post_id": post_id, "error": None}
        else:
            return {
                "success": False,
                "post_id": None,
                "error":   f"HTTP {response.status_code}: {response.text}",
            }

    except Exception as e:
        return {"success": False, "post_id": None, "error": str(e)}