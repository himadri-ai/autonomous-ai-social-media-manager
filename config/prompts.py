# config/prompts.py
# All LLM prompt templates live here.
# Edit the tone definitions or post structure here without touching agent code.

TONE_DESCRIPTIONS = {
    "Educational":     "informative, clear, and structured with key takeaways",
    "Motivational":    "inspiring, energetic, and action-oriented",
    "Promotional":     "persuasive, benefit-focused, and with a clear call to action",
    "Storytelling":    "narrative-driven, personal, and emotionally engaging",
    "Thought Leadership": "opinionated, insight-driven, and forward-looking",
}

LONG_POST_PROMPT = """
You are a professional social media copywriter specializing in LinkedIn and Facebook content.

Your task is to write a long-form social media post based on the inputs below.

INPUTS:
- Topic Keywords: {keywords}
- Tone: {tone} ({tone_description})
- Target Audience: {audience}

RULES:
- Maximum 1000 characters including spaces
- Start with a strong hook in the first line that stops the scroll
- Use short paragraphs of 1 to 2 lines each
- Include 3 to 5 relevant hashtags at the end
- Do NOT use buzzwords like "game-changer" or "synergy"
- End with a clear call to action or a question to drive comments
- Return ONLY the post text, no explanations or labels

Write the post now:
"""

SHORT_POST_PROMPT = """
You are a professional social media copywriter specializing in short-form content.

Your task is to write a short social media post based on the inputs below.

INPUTS:
- Topic Keywords: {keywords}
- Tone: {tone} ({tone_description})
- Target Audience: {audience}

RULES:
- Maximum 150 characters including spaces
- Must be punchy and self-contained in one or two lines
- Include 1 to 2 relevant hashtags within the character limit
- No emojis unless they add clear meaning
- Return ONLY the post text, no explanations or labels

Write the post now:
"""


def build_long_prompt(keywords: str, tone: str, audience: str) -> str:
    """
    Returns the filled long-form prompt string ready to send to the LLM.
    """
    tone_description = TONE_DESCRIPTIONS.get(tone, "clear and professional")
    return LONG_POST_PROMPT.format(
        keywords=keywords,
        tone=tone,
        tone_description=tone_description,
        audience=audience,
    )


def build_short_prompt(keywords: str, tone: str, audience: str) -> str:
    """
    Returns the filled short-form prompt string ready to send to the LLM.
    """
    tone_description = TONE_DESCRIPTIONS.get(tone, "clear and professional")
    return SHORT_POST_PROMPT.format(
        keywords=keywords,
        tone=tone,
        tone_description=tone_description,
        audience=audience,
    )