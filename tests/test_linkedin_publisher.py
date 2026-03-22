# tests/test_linkedin_publisher.py
# Tests for linkedin_publisher.py using mocked HTTP calls.
# No real LinkedIn credentials or network calls needed.

from unittest.mock import patch, MagicMock
from publishers.linkedin_publisher import post_to_linkedin


def make_mock_response(status_code: int, json_data: dict = None, headers: dict = None, text: str = "") -> MagicMock:
    """Builds a fake requests.Response object."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data or {}
    mock_resp.headers = headers or {}
    mock_resp.text = text
    return mock_resp


class TestPostToLinkedin:

    @patch("publishers.linkedin_publisher.LINKEDIN_ACCESS_TOKEN", "fake_token")
    @patch("publishers.linkedin_publisher.LINKEDIN_PERSON_URN", "urn:li:person:fake")
    @patch("publishers.linkedin_publisher.requests.post")
    def test_text_only_post_success(self, mock_post):
        """Text-only post returns success when API responds 201."""
        mock_post.return_value = make_mock_response(
            status_code=201,
            headers={"x-restli-id": "post_abc123"},
        )

        result = post_to_linkedin("This is a test LinkedIn post. #AI")

        assert result["success"] is True
        assert result["post_id"] == "post_abc123"
        assert result["error"] is None

    @patch("publishers.linkedin_publisher.LINKEDIN_ACCESS_TOKEN", "fake_token")
    @patch("publishers.linkedin_publisher.LINKEDIN_PERSON_URN", "urn:li:person:fake")
    @patch("publishers.linkedin_publisher.requests.post")
    def test_api_error_returns_failure(self, mock_post):
        """If LinkedIn API returns non-201, success must be False."""
        mock_post.return_value = make_mock_response(
            status_code=401,
            text="Unauthorized",
        )

        result = post_to_linkedin("Test post")

        assert result["success"] is False
        assert "401" in result["error"]
        assert result["post_id"] is None

    @patch("publishers.linkedin_publisher.LINKEDIN_ACCESS_TOKEN", "")
    @patch("publishers.linkedin_publisher.LINKEDIN_PERSON_URN", "")
    def test_missing_credentials_returns_failure(self):
        """If credentials are empty, must fail gracefully without making API call."""
        result = post_to_linkedin("Test post")

        assert result["success"] is False
        assert "not configured" in result["error"]

    @patch("publishers.linkedin_publisher.LINKEDIN_ACCESS_TOKEN", "fake_token")
    @patch("publishers.linkedin_publisher.LINKEDIN_PERSON_URN", "urn:li:person:fake")
    @patch("publishers.linkedin_publisher.requests.post")
    def test_network_exception_returns_failure(self, mock_post):
        """If a network error occurs, error key must contain the exception message."""
        mock_post.side_effect = Exception("Connection timeout")

        result = post_to_linkedin("Test post")

        assert result["success"] is False
        assert "Connection timeout" in result["error"]

    @patch("publishers.linkedin_publisher.LINKEDIN_ACCESS_TOKEN", "fake_token")
    @patch("publishers.linkedin_publisher.LINKEDIN_PERSON_URN", "urn:li:person:fake")
    @patch("publishers.linkedin_publisher._upload_image")
    @patch("publishers.linkedin_publisher.requests.post")
    def test_post_with_image_success(self, mock_post, mock_upload):
        """Post with image attaches asset URN and returns success."""
        mock_upload.return_value = "urn:li:digitalmediaAsset:fake123"
        mock_post.return_value = make_mock_response(
            status_code=201,
            headers={"x-restli-id": "post_img_456"},
        )

        result = post_to_linkedin("Test post with image", image_bytes=b"fake_image_data")

        assert result["success"] is True
        assert result["post_id"] == "post_img_456"

    @patch("publishers.linkedin_publisher.LINKEDIN_ACCESS_TOKEN", "fake_token")
    @patch("publishers.linkedin_publisher.LINKEDIN_PERSON_URN", "urn:li:person:fake")
    @patch("publishers.linkedin_publisher._upload_image")
    @patch("publishers.linkedin_publisher.requests.post")
    def test_post_falls_back_to_text_if_image_upload_fails(self, mock_post, mock_upload):
        """If image upload fails, post should still go out as text-only."""
        mock_upload.return_value = None  # upload failed
        mock_post.return_value = make_mock_response(
            status_code=201,
            headers={"x-restli-id": "post_textonly_789"},
        )

        result = post_to_linkedin("Test post", image_bytes=b"fake_image_data")

        assert result["success"] is True