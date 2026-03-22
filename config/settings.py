# config/settings.py
# Loads all environment variables and exposes them as typed constants.
# Every other file imports from here. Never import os.environ directly elsewhere.

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3-8b-8192")

# --- LinkedIn ---
LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_PERSON_URN: str = os.getenv("LINKEDIN_PERSON_URN", "")

# --- Facebook ---
FACEBOOK_PAGE_ACCESS_TOKEN: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")

# --- App ---
POST_HISTORY_PATH: str = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "post_history.json"
)


def validate_settings() -> dict:
    """
    Checks which API keys are present and properly set.
    Returns a dict with status per service so the UI can warn the user.
    """
    placeholder_fragments = ["your_", "_here", "placeholder"]

    def is_real(value: str) -> bool:
        if not value:
            return False
        for fragment in placeholder_fragments:
            if fragment in value.lower():
                return False
        return True

    return {
        "groq":     is_real(GROQ_API_KEY),
        "linkedin": is_real(LINKEDIN_ACCESS_TOKEN) and is_real(LINKEDIN_PERSON_URN),
        "facebook": is_real(FACEBOOK_PAGE_ACCESS_TOKEN) and is_real(FACEBOOK_PAGE_ID),
    }