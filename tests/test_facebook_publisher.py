# tests/test_facebook_publisher.py
# Tests for facebook_publisher.py using mocked HTTP calls.
# No real Facebook credentials or network calls needed.

from unittest.mock import patch, MagicMock
from publishers.facebook_publisher import post_to_facebook


def make_mock_response(status_code: int, json_data: dict = None, text: str = "") -> MagicMock:
    """Builds a fake requests.Response object."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data or {}
    mock_resp.text = text
    return mock_resp


class TestPostToFacebook:

    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ACCESS_TOKEN", "fake_token")
    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ID", "123456789")
    @patch("publishers.facebook_publisher.requests.post")
    def test_text_only_post_success(self, mock_post):
        """Text-only post returns success when API responds 200 with an id."""
        mock_post.return_value = make_mock_response(
            status_code=200,
            json_data={"id": "123456789_987654321"},
        )

        result = post_to_facebook("This is a test Facebook post. #AI")

        assert result["success"] is True
        assert result["post_id"] == "123456789_987654321"
        assert result["error"] is None

    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ACCESS_TOKEN", "fake_token")
    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ID", "123456789")
    @patch("publishers.facebook_publisher.requests.post")
    def test_image_post_success(self, mock_post):
        """Image post returns success when API responds 200 with an id."""
        mock_post.return_value = make_mock_response(
            status_code=200,
            json_data={"id": "123456789_111222333"},
        )

        result = post_to_facebook("Test post with image", image_bytes=b"fake_image_data")

        assert result["success"] is True
        assert result["post_id"] == "123456789_111222333"
        assert result["error"] is None

    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ACCESS_TOKEN", "fake_token")
    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ID", "123456789")
    @patch("publishers.facebook_publisher.requests.post")
    def test_api_error_returns_failure(self, mock_post):
        """If Facebook API returns an error response, success must be False."""
        mock_post.return_value = make_mock_response(
            status_code=400,
            json_data={
                "error": {
                    "message": "Invalid OAuth access token",
                    "type": "OAuthException",
                    "code": 190,
                }
            },
        )

        result = post_to_facebook("Test post")

        assert result["success"] is False
        assert "Invalid OAuth access token" in result["error"]
        assert result["post_id"] is None

    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ACCESS_TOKEN", "")
    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ID", "")
    def test_missing_credentials_returns_failure(self):
        """If credentials are empty, must fail gracefully without making API call."""
        result = post_to_facebook("Test post")

        assert result["success"] is False
        assert "not configured" in result["error"]

    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ACCESS_TOKEN", "fake_token")
    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ID", "123456789")
    @patch("publishers.facebook_publisher.requests.post")
    def test_network_exception_returns_failure(self, mock_post):
        """If a network error occurs, error key must contain the exception message."""
        mock_post.side_effect = Exception("Connection refused")

        result = post_to_facebook("Test post")

        assert result["success"] is False
        assert "Connection refused" in result["error"]

    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ACCESS_TOKEN", "fake_token")
    @patch("publishers.facebook_publisher.FACEBOOK_PAGE_ID", "123456789")
    @patch("publishers.facebook_publisher.requests.post")
    def test_response_without_id_returns_failure(self, mock_post):
        """If API returns 200 but no id field, treat as failure."""
        mock_post.return_value = make_mock_response(
            status_code=200,
            json_data={"result": "true"},  # no "id" key
        )

        result = post_to_facebook("Test post")

        assert result["success"] is False