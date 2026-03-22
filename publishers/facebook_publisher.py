# publishers/facebook_publisher.py
# Handles all Facebook Graph API interactions.
# Requires a Facebook Page (not personal profile) and a Page Access Token.
# Supports text-only posts and text + image posts.

import requests
from config.settings import FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID

API_BASE = "https://graph.facebook.com/v19.0"


def post_to_facebook(text: str, image_bytes: bytes | None = None) -> dict:
    """
    Posts to a Facebook Page. Supports text-only or text + image.

    For text-only:  calls /PAGE_ID/feed
    For image post: calls /PAGE_ID/photos which publishes image + caption together
                    in a single API call (simpler than LinkedIn).

    Args:
        text:        The post copy.
        image_bytes: Optional raw image bytes. Pass None for text-only post.

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
        if image_bytes:
            # Image post: single multipart call to /photos endpoint
            response = requests.post(
                f"{API_BASE}/{FACEBOOK_PAGE_ID}/photos",
                data={
                    "caption":      text,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
                },
                files={
                    "source": ("image.jpg", image_bytes, "image/jpeg"),
                },
                timeout=30,
            )
        else:
            # Text-only post: single JSON call to /feed endpoint
            response = requests.post(
                f"{API_BASE}/{FACEBOOK_PAGE_ID}/feed",
                json={
                    "message":      text,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
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
            error_message = data.get("error", {}).get("message", response.text)
            return {
                "success": False,
                "post_id": None,
                "error":   f"HTTP {response.status_code}: {error_message}",
            }

    except Exception as e:
        return {
            "success": False,
            "post_id": None,
            "error":   str(e),
        }