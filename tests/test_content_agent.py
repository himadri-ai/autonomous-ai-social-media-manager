# tests/test_content_agent.py
# Tests for content_agent.py using mocked LLM responses.
# These tests run instantly with no real API calls and no Groq key needed.


from unittest.mock import patch, MagicMock


# --- Helpers ---

def make_mock_response(text: str) -> MagicMock:
    """Builds a fake Groq API response object matching the real response shape."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = text
    return mock_response


# --- Tests ---

class TestGeneratePosts:

    @patch("agents.content_agent.client")
    def test_returns_both_variants(self, mock_client):
        """Happy path: both long and short posts are returned."""
        mock_client.chat.completions.create.side_effect = [
            make_mock_response("This is a long post about AI consulting. " * 10),
            make_mock_response("Short AI post. #AI"),
        ]

        from agents.content_agent import generate_posts
        result = generate_posts("AI consulting", "Educational", "HR managers")

        assert result["error"] is None
        assert len(result["long_post"]) > 0
        assert len(result["short_post"]) > 0

    @patch("agents.content_agent.client")
    def test_long_post_within_character_limit(self, mock_client):
        """Long post must never exceed 3000 characters even if LLM returns more."""
        mock_client.chat.completions.create.side_effect = [
            make_mock_response("A" * 3000),   # LLM returns way too much
            make_mock_response("Short post. #AI"),
        ]

        from agents.content_agent import generate_posts
        result = generate_posts("AI consulting", "Motivational", "founders")

        assert result["long_char_count"] <= 3000

    @patch("agents.content_agent.client")
    def test_short_post_within_character_limit(self, mock_client):
        """Short post must never exceed 250 characters even if LLM returns more."""
        mock_client.chat.completions.create.side_effect = [
            make_mock_response("Valid long post content here."),
            make_mock_response("B" * 500),   # LLM returns way too much
        ]

        from agents.content_agent import generate_posts
        result = generate_posts("AI consulting", "Promotional", "CTOs")

        assert result["short_char_count"] <= 250

    @patch("agents.content_agent.client")
    def test_char_counts_match_actual_length(self, mock_client):
        """Reported char counts must match actual string lengths."""
        mock_client.chat.completions.create.side_effect = [
            make_mock_response("Long post content here."),
            make_mock_response("Short post. #AI"),
        ]

        from agents.content_agent import generate_posts
        result = generate_posts("AI consulting", "Storytelling", "executives")

        assert result["long_char_count"]  == len(result["long_post"])
        assert result["short_char_count"] == len(result["short_post"])

    @patch("agents.content_agent.client")
    def test_returns_error_on_api_failure(self, mock_client):
        """If Groq API throws, error key must contain the message and posts must be empty."""
        mock_client.chat.completions.create.side_effect = Exception("API timeout")

        from agents.content_agent import generate_posts
        result = generate_posts("AI consulting", "Educational", "HR managers")

        assert result["error"] == "API timeout"
        assert result["long_post"]  == ""
        assert result["short_post"] == ""

    @patch("agents.content_agent.client")
    def test_all_tones_accepted(self, mock_client):
        """All five tone options must produce a valid result without errors."""
        tones = ["Educational", "Motivational", "Promotional", "Storytelling", "Thought Leadership"]

        for tone in tones:
            mock_client.chat.completions.create.side_effect = [
                make_mock_response(f"Long post for {tone}."),
                make_mock_response(f"Short. #{tone[:4]}"),
            ]

            from agents.content_agent import generate_posts
            result = generate_posts("AI consulting", tone, "professionals")

            assert result["error"] is None, f"Tone '{tone}' caused an error: {result['error']}"