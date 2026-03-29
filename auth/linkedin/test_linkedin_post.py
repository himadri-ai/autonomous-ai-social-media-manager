# auth/linkedin/test_linkedin_post.py
# Tests LinkedIn posting with text only, text + image, or text + video.
# Run from project root:
#   python auth/linkedin/test_linkedin_post.py
#
# INSTRUCTIONS:
# Set MEDIA_PATH to a file path relative to the project root to test with media.
# Examples:
#   MEDIA_PATH = "auth/linkedin/test_image.jpg"   -- image post
#   MEDIA_PATH = "auth/linkedin/test_video.mp4"   -- video post
#   MEDIA_PATH = None                              -- text only

import os
import sys

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv  # noqa: E402
from publishers.linkedin_publisher import post_to_linkedin, _detect_media_type  # noqa: E402
from config.settings import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN  # noqa: E402

load_dotenv()

# ---------------------------------------------------------------------------
# Set your media file path here
# ---------------------------------------------------------------------------
MEDIA_PATH = "auth/linkedin/dario.jpg"

# ---------------------------------------------------------------------------
# Validate credentials
# ---------------------------------------------------------------------------
print("\n=== LinkedIn Live Post Test ===\n")

if not LINKEDIN_ACCESS_TOKEN or "placeholder" in LINKEDIN_ACCESS_TOKEN.lower():
    print("ERROR: LINKEDIN_ACCESS_TOKEN not set in .env")
    sys.exit(1)

if not LINKEDIN_PERSON_URN or "placeholder" in LINKEDIN_PERSON_URN.lower():
    print("ERROR: LINKEDIN_PERSON_URN not set in .env")
    sys.exit(1)

print(f"Token loaded:      {LINKEDIN_ACCESS_TOKEN[:10]}...")
print(f"Person URN loaded: {LINKEDIN_PERSON_URN}")

# ---------------------------------------------------------------------------
# Load media if provided
# ---------------------------------------------------------------------------
image_bytes = None
video_bytes = None
filename    = ""
media_type  = "none"

if MEDIA_PATH:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    abs_path     = os.path.join(project_root, MEDIA_PATH)

    if not os.path.exists(abs_path):
        print(f"\nERROR: Media file not found at: {abs_path}")
        sys.exit(1)

    filename   = os.path.basename(MEDIA_PATH)
    media_type = _detect_media_type(filename)

    if media_type == "unknown":
        print(f"\nERROR: Unsupported file type: {filename}")
        print("Supported: JPG, JPEG, PNG, GIF, WEBP, MP4, MOV, AVI, MKV")
        sys.exit(1)

    with open(abs_path, "rb") as f:
        raw_bytes = f.read()

    file_size_mb = len(raw_bytes) / (1024 * 1024)

    if media_type == "image":
        image_bytes = raw_bytes
        print(f"Image loaded:      {filename} ({file_size_mb:.1f} MB)")
    elif media_type == "video":
        video_bytes = raw_bytes
        print(f"Video loaded:      {filename} ({file_size_mb:.1f} MB)")
        if file_size_mb > 200:
            print("WARNING: LinkedIn recommends videos under 200 MB for best results.")
else:
    print("Media:             None (text-only post)")

# ---------------------------------------------------------------------------
# Test post content
# ---------------------------------------------------------------------------
TEST_POST = """ In a world racing blindly toward AI dominance, 
one man chose conscience over convenience.

Dario Amodei -- physicist, biophysicist, and now 
the quiet storm reshaping artificial intelligence 
didn't leave OpenAI for fame. 

He left because he believed the world deserved better.

A devoted runner and science lover outside the office, 
Dario co-founded Anthropic in 2021 with his sister Daniela, 
turning a moral conviction into the 
fastest-growing software company in history.

💡 When the Pentagon asked him to lift Claude's 
ban on mass surveillance & autonomous weapons, 
Dario said NO !! 
even at the cost of being labeled a "supply-chain risk." 
That's not stubbornness. That's integrity.

And the results speak volumes:
📈 Revenue: $0 → $100M → $1B → $4.5B+ (annualized)
🏆 Named Time's Most Influential Person 2025
💰 Anthropic valued at $380 Billion

Claude isn't just another chatbot. 
It's reshaping how enterprises think, code, and create 
-- where OpenAI chases virality and Gemini chases scale, 
Anthropic is chasing something rarer: TRUST!!.

In the AI race, Dario Amodei isn't just building the future. 
He's building it responsibly. 🔥

#AI #Anthropic #Claude #DarioAmodei #FutureOfWork #AISafety #Leadership"""

post_type = {"none": "Text Only", "image": "Text + Image", "video": "Text + Video"}[media_type]
print(f"\nPost type:         {post_type}")
print(f"Character count:   {len(TEST_POST)}")
print(f"\nPost content:\n{'-'*40}")
print(TEST_POST)
print(f"{'-'*40}")

# ---------------------------------------------------------------------------
# Confirm before posting
# ---------------------------------------------------------------------------
confirm = input("\nThis will post LIVE to your LinkedIn profile. Type 'yes' to confirm: ").strip().lower()

if confirm != "yes":
    print("Cancelled. No post was made.")
    sys.exit(0)

# ---------------------------------------------------------------------------
# Fire the post
# ---------------------------------------------------------------------------
print(f"\nPosting to LinkedIn ({post_type})...")

if media_type == "video":
    print("Video upload may take 30-60 seconds depending on file size...")

result = post_to_linkedin(
    TEST_POST,
    image_bytes=image_bytes,
    video_bytes=video_bytes,
    filename=filename,
)

if result["success"]:
    print("\nSUCCESS! Post is live on your LinkedIn profile.")
    print(f"Post ID: {result['post_id']}")
    print("\nOpen LinkedIn in your browser to verify the post is showing.")
    if media_type == "video":
        print("Note: LinkedIn may take a few minutes to process the video.")
else:
    print(f"\nFAILED: {result['error']}")
    print("\nCommon causes:")
    print("  - Token expired (run get_linkedin_token.py again)")
    print("  - Wrong Person URN in .env")
    print("  - Image/video format not supported")
    print("  - Share on LinkedIn product not approved in Developer App")
    print("  - Video file too large (max 5GB, recommended under 200MB)")