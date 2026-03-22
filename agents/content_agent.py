# agents/content_agent.py
# Calls the Groq LLM and returns both long and short post variants.
# This is the only file that talks to the LLM directly.

from groq import Groq
from config.settings import GROQ_API_KEY, LLM_MODEL
from config.prompts import build_long_prompt, build_short_prompt


client = Groq(api_key=GROQ_API_KEY)


def _call_llm(prompt: str) -> str:
    """
    Sends a single prompt to Groq and returns the response text.
    Raises an exception if the API call fails.
    """
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional social media copywriter. "
                    "Follow all instructions precisely. "
                    "Return only the requested content with no extra commentary."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def generate_posts(keywords: str, tone: str, audience: str) -> dict:
    """
    Main function called by the UI.
    Takes user inputs and returns both post variants.

    Returns:
        {
            "long_post":  str,   # up to 1000 characters
            "short_post": str,   # up to 150 characters
            "long_char_count":  int,
            "short_char_count": int,
            "error": None or str
        }
    """
    try:
        long_prompt  = build_long_prompt(keywords, tone, audience)
        short_prompt = build_short_prompt(keywords, tone, audience)

        long_post  = _call_llm(long_prompt)
        short_post = _call_llm(short_prompt)

        # Enforce hard character limits as a safety net
        long_post  = long_post[:1000]
        short_post = short_post[:150]

        return {
            "long_post":        long_post,
            "short_post":       short_post,
            "long_char_count":  len(long_post),
            "short_char_count": len(short_post),
            "error":            None,
        }

    except Exception as e:
        return {
            "long_post":        "",
            "short_post":       "",
            "long_char_count":  0,
            "short_char_count": 0,
            "error":            str(e),
        }