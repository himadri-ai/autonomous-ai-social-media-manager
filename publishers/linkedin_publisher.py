# publishers/linkedin_publisher.py
# Handles all LinkedIn API interactions.
# Supports text-only posts and text + image posts.

import requests
from config.settings import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN

API_BASE = "https://api.linkedin.com/v2"

HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}


def _upload_image(image_bytes: bytes) -> str | None:
    """
    Uploads an image to LinkedIn and returns the asset URN.
    Returns None if upload fails.

    Step 1: Register the image upload and get an upload URL.
    Step 2: PUT the image bytes to that URL.
    Step 3: Return the asset URN for attaching to the post.
    """
    # Step 1: Register upload
    register_payload = {
        "registerUploadRequest": {
            "owner": LINKEDIN_PERSON_URN,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [
                {
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER",
                }
            ],
        }
    }

    register_response = requests.post(
        f"{API_BASE}/assets?action=registerUpload",
        headers=HEADERS,
        json=register_payload,
        timeout=10,
    )

    if register_response.status_code != 200:
        return None

    data = register_response.json()
    upload_url = data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset_urn = data["value"]["asset"]

    # Step 2: Upload the image bytes
    upload_response = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"},
        data=image_bytes,
        timeout=30,
    )

    if upload_response.status_code not in (200, 201):
        return None

    return asset_urn


def post_to_linkedin(text: str, image_bytes: bytes | None = None) -> dict:
    """
    Posts to LinkedIn. Supports text-only or text + image.

    Args:
        text:        The post copy, max 1000 characters.
        image_bytes: Optional raw image bytes. Pass None for text-only post.

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
        # Build the base post payload
        payload = {
            "author": LINKEDIN_PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        # If image provided, upload it and attach to payload
        if image_bytes:
            asset_urn = _upload_image(image_bytes)
            if asset_urn:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "shareMediaCategory"
                ] = "IMAGE"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "media"
                ] = [
                    {
                        "status": "READY",
                        "media":  asset_urn,
                    }
                ]

        response = requests.post(
            f"{API_BASE}/ugcPosts",
            headers=HEADERS,
            json=payload,
            timeout=15,
        )

        if response.status_code == 201:
            post_id = response.headers.get("x-restli-id", "unknown")
            return {
                "success": True,
                "post_id": post_id,
                "error":   None,
            }
        else:
            return {
                "success": False,
                "post_id": None,
                "error":   f"HTTP {response.status_code}: {response.text}",
            }

    except Exception as e:
        return {
            "success": False,
            "post_id": None,
            "error":   str(e),
        }