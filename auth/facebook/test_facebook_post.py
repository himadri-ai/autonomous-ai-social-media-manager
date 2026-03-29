# auth/facebook/test_facebook_post.py
# Tests Facebook Page posting with text only, text + image, or text + video.
# Run from project root:
#   python auth/facebook/test_facebook_post.py
#
# INSTRUCTIONS:
# Set MEDIA_PATH to a file path relative to project root to test with media.
# Examples:
#   MEDIA_PATH = "auth/facebook/test_image.jpg"   -- image post
#   MEDIA_PATH = "auth/facebook/test_video.mp4"   -- video post
#   MEDIA_PATH = None                              -- text only

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv  # noqa: E402
from publishers.facebook_publisher import post_to_facebook  # noqa: E402
from config.settings import FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID  # noqa: E402

load_dotenv()

# ---------------------------------------------------------------------------
# Set your media file path here
# ---------------------------------------------------------------------------
MEDIA_PATH = None

# ---------------------------------------------------------------------------
# Validate credentials
# ---------------------------------------------------------------------------
print("\n=== Facebook Live Post Test ===\n")

if not FACEBOOK_PAGE_ACCESS_TOKEN or "placeholder" in FACEBOOK_PAGE_ACCESS_TOKEN.lower():
    print("ERROR: FACEBOOK_PAGE_ACCESS_TOKEN not set in .env")
    sys.exit(1)

if not FACEBOOK_PAGE_ID or "placeholder" in FACEBOOK_PAGE_ID.lower():
    print("ERROR: FACEBOOK_PAGE_ID not set in .env")
    sys.exit(1)

print(f"Token loaded:    {FACEBOOK_PAGE_ACCESS_TOKEN[:10]}...")
print(f"Page ID loaded:  {FACEBOOK_PAGE_ID}")

# ---------------------------------------------------------------------------
# Load media if provided
# ---------------------------------------------------------------------------
image_bytes = None
media_type  = "none"

if MEDIA_PATH:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    abs_path     = os.path.join(project_root, MEDIA_PATH)

    if not os.path.exists(abs_path):
        print(f"\nERROR: Media file not found at: {abs_path}")
        sys.exit(1)

    filename   = os.path.basename(MEDIA_PATH)
    ext        = os.path.splitext(filename.lower())[1]

    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    video_exts = {".mp4", ".mov", ".avi"}

    if ext in image_exts:
        media_type = "image"
    elif ext in video_exts:
        media_type = "video"
    else:
        print(f"\nERROR: Unsupported file type: {filename}")
        sys.exit(1)

    with open(abs_path, "rb") as f:
        image_bytes = f.read()

    file_size_mb = len(image_bytes) / (1024 * 1024)
    print(f"Media loaded:    {filename} ({file_size_mb:.1f} MB) -- {media_type}")
else:
    print("Media:           None (text-only post)")

# ---------------------------------------------------------------------------
# Test post content
# ---------------------------------------------------------------------------
TEST_POST = """🤔 67% of recruiters say they spend
more time on admin than hiring.

That is the real talent crisis.
Not a shortage of candidates.
A shortage of recruiter time.

→ AI screens resumes in seconds
→ AI schedules interviews automatically
→ AI answers candidate FAQs 24/7
→ AI drafts offer letters instantly

Free your recruiters to do one thing.
Build relationships with great talent.

Source: LinkedIn Global Talent Trends (linkedin.com/talent-solutions)

What is the biggest time drain in your hiring process?

Follow Himadri Sen for practical AI consulting insights. 😎

#AIRecruitment #HRAutomation #FutureOfWork #AIinHR"""

post_type = {"none": "Text Only", "image": "Text + Image", "video": "Text + Video"}[media_type]
print(f"\nPost type:       {post_type}")
print(f"Character count: {len(TEST_POST)}")
print(f"\nPost content:\n{'-'*40}")
print(TEST_POST)
print(f"{'-'*40}")

# ---------------------------------------------------------------------------
# Confirm before posting
# ---------------------------------------------------------------------------
confirm = input("\nThis will post LIVE to your Facebook Page. Type 'yes' to confirm: ").strip().lower()

if confirm != "yes":
    print("Cancelled. No post was made.")
    sys.exit(0)

# ---------------------------------------------------------------------------
# Fire the post
# ---------------------------------------------------------------------------
print(f"\nPosting to Facebook ({post_type})...")
result = post_to_facebook(TEST_POST, image_bytes=image_bytes)

if result["success"]:
    print("\nSUCCESS! Post is live on your Facebook Page.")
    print(f"Post ID: {result['post_id']}")
    print("\nOpen your Facebook Page in your browser to verify.")
else:
    print(f"\nFAILED: {result['error']}")
    print("\nCommon causes:")
    print("  - Token expired -- run get_facebook_token.py to refresh")
    print("  - Wrong Page ID in .env")
    print("  - App not published or missing pages_manage_posts permission")
    print("  - Image format not supported (use JPG or PNG)")