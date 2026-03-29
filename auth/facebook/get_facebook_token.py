# auth/facebook/get_facebook_token.py
# Exchanges your short-lived Page Access Token for a long-lived one.
# Long-lived tokens last ~60 days instead of ~1 hour.
# Run this whenever your token expires.
#
# Usage (run from project root):
#   python auth/facebook/get_facebook_token.py
#
# Prerequisites:
#   FACEBOOK_PAGE_ACCESS_TOKEN -- short-lived token from Graph API Explorer
#   FACEBOOK_APP_ID            -- from Meta Developer App Settings > Basic
#   FACEBOOK_APP_SECRET        -- from Meta Developer App Settings > Basic
#   FACEBOOK_PAGE_ID           -- your Facebook Page numeric ID

import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

PAGE_TOKEN  = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
APP_ID      = os.getenv("FACEBOOK_APP_ID", "").strip()
APP_SECRET  = os.getenv("FACEBOOK_APP_SECRET", "").strip()
PAGE_ID     = os.getenv("FACEBOOK_PAGE_ID", "").strip()

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
print("\n=== Facebook Long-Lived Token Generator ===\n")

missing = []
if not PAGE_TOKEN or "placeholder" in PAGE_TOKEN.lower():
    missing.append("FACEBOOK_PAGE_ACCESS_TOKEN")
if not APP_ID or "placeholder" in APP_ID.lower():
    missing.append("FACEBOOK_APP_ID")
if not APP_SECRET or "placeholder" in APP_SECRET.lower():
    missing.append("FACEBOOK_APP_SECRET")
if not PAGE_ID or "placeholder" in PAGE_ID.lower():
    missing.append("FACEBOOK_PAGE_ID")

if missing:
    print("ERROR: Missing values in .env:")
    for m in missing:
        print(f"  - {m}")
    sys.exit(1)

print(f"App ID loaded:         {APP_ID}")
print(f"Page ID loaded:        {PAGE_ID}")
print(f"Short token loaded:    {PAGE_TOKEN[:10]}...")

# ---------------------------------------------------------------------------
# Step 1: Exchange short-lived user token for long-lived user token
# ---------------------------------------------------------------------------
print("\nStep 1: Exchanging for long-lived user token...")

response = requests.get(
    "https://graph.facebook.com/v25.0/oauth/access_token",
    params={
        "grant_type":        "fb_exchange_token",
        "client_id":         APP_ID,
        "client_secret":     APP_SECRET,
        "fb_exchange_token": PAGE_TOKEN,
    },
    timeout=15,
)

data = response.json()

if "access_token" not in data:
    print(f"\nERROR: {data}")
    print("\nMake sure your FACEBOOK_PAGE_ACCESS_TOKEN is a fresh token")
    print("from the Graph API Explorer (generated within the last hour).")
    sys.exit(1)

long_lived_user_token = data["access_token"]
print(f"Long-lived user token obtained: {long_lived_user_token[:10]}...")

# ---------------------------------------------------------------------------
# Step 2: Get permanent Page Access Token via /me/accounts
# ---------------------------------------------------------------------------
print("\nStep 2: Getting permanent Page Access Token via /me/accounts...")

accounts_response = requests.get(
    "https://graph.facebook.com/v25.0/me/accounts",
    params={
        "access_token": long_lived_user_token,
    },
    timeout=15,
)

accounts_data = accounts_response.json()

if "data" not in accounts_data or not accounts_data["data"]:
    print(f"\nERROR: {accounts_data}")
    print("\nMake sure your Facebook Page is linked to your personal account.")
    sys.exit(1)

# Find the matching page by ID
permanent_page_token = None
page_name            = None

for page in accounts_data["data"]:
    if page.get("id") == PAGE_ID:
        permanent_page_token = page["access_token"]
        page_name            = page["name"]
        break

# If exact ID not found, use the first page and show available pages
if not permanent_page_token:
    print("\nWARNING: Could not match PAGE_ID exactly. Available pages:")
    for page in accounts_data["data"]:
        print(f"  ID: {page['id']} -- Name: {page['name']}")
    print(f"\nYour .env PAGE_ID is: {PAGE_ID}")
    print("Update FACEBOOK_PAGE_ID in .env to match one of the IDs above.")
    sys.exit(1)

print(f"Page name:              {page_name}")
print(f"Permanent token:        {permanent_page_token[:10]}...")

# ---------------------------------------------------------------------------
# Step 3: Verify token works by fetching page info
# ---------------------------------------------------------------------------
print("\nStep 3: Verifying token...")

verify = requests.get(
    f"https://graph.facebook.com/v25.0/{PAGE_ID}",
    params={
        "fields":       "name,fan_count",
        "access_token": permanent_page_token,
    },
    timeout=15,
)

verify_data = verify.json()

if "name" not in verify_data:
    print(f"\nERROR verifying token: {verify_data}")
    sys.exit(1)

print(f"Verified page:          {verify_data['name']}")

# ---------------------------------------------------------------------------
# Step 4: Print value to copy into .env
# ---------------------------------------------------------------------------
print("\n=== SUCCESS -- Update your .env file ===\n")
print(f"FACEBOOK_PAGE_ACCESS_TOKEN={permanent_page_token}")
print("\nThis token does not expire as long as your app stays active.")
print("If it ever stops working, run this script again with a fresh")
print("short-lived token from the Graph API Explorer.\n")