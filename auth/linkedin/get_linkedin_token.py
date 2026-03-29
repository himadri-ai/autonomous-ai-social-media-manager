# auth/linkedin/get_linkedin_token.py
# Run this ONCE to get your LinkedIn access token and Person URN.
# Paste the values into your .env file when done.

import os
import sys
import urllib.parse
import requests
from urllib.parse import urlparse, parse_qs

# Allow HTTP on localhost for development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID     = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
REDIRECT_URI  = "http://localhost:8502"
SCOPES        = "openid profile w_member_social"

AUTH_URL  = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
if not CLIENT_ID or not CLIENT_SECRET:
    print("\nERROR: LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET not found in .env")
    sys.exit(1)

print(f"\nClient ID loaded:     {CLIENT_ID[:8]}...")
print(f"Client Secret loaded: {CLIENT_SECRET[:4]}...")

# ---------------------------------------------------------------------------
# Step 1: Build authorization URL manually
# ---------------------------------------------------------------------------

params = {
    "response_type": "code",
    "client_id":     CLIENT_ID,
    "redirect_uri":  REDIRECT_URI,
    "scope":         SCOPES,
    "state":         "random_state_123",
}
auth_url = AUTH_URL + "?" + urllib.parse.urlencode(params)

print("\n=== Step 1: Open this URL in your browser and click Allow ===\n")
print(auth_url)

# ---------------------------------------------------------------------------
# Step 2: Get the authorization code from redirected URL
# ---------------------------------------------------------------------------
print("\n=== Step 2: After clicking Allow ===")
print("Your browser will redirect to localhost and show an error page.")
print("That is expected. Copy the FULL URL from the address bar.\n")

redirected_url = input("Paste the full redirected URL here: ").strip()

# Parse the code cleanly using urllib
parsed = urlparse(redirected_url)
params = parse_qs(parsed.query)

if "code" not in params:
    print("\nERROR: No 'code' found in the URL you pasted.")
    print(f"URL received: {redirected_url}")
    print("Make sure you copied the complete URL from the browser address bar.")
    sys.exit(1)

auth_code = params["code"][0]
print(f"\nAuthorization code extracted: {auth_code[:10]}...")

# ---------------------------------------------------------------------------
# Step 3: Exchange code for access token via direct POST
# ---------------------------------------------------------------------------
print("\nExchanging code for access token...")

response = requests.post(
    TOKEN_URL,
    data={
        "grant_type":    "authorization_code",
        "code":          auth_code,
        "redirect_uri":  REDIRECT_URI,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
    },
)

token_data = response.json()

if "access_token" not in token_data:
    print("\nERROR getting token.")
    print(f"Status code: {response.status_code}")
    print(f"Response: {token_data}")
    sys.exit(1)

access_token = token_data["access_token"]
print("Access token obtained successfully.")

# ---------------------------------------------------------------------------
# Step 4: Fetch Person URN
# ---------------------------------------------------------------------------
print("Fetching your LinkedIn Person URN...")

userinfo = requests.get(
    "https://api.linkedin.com/v2/userinfo",
    headers={"Authorization": f"Bearer {access_token}"},
).json()

sub = userinfo.get("sub", "")
if not sub:
    print(f"\nERROR: Could not retrieve sub. Response: {userinfo}")
    sys.exit(1)

person_urn = f"urn:li:person:{sub}"
name       = userinfo.get("name", "Unknown")
print(f"Authenticated as: {name}")

# ---------------------------------------------------------------------------
# Step 5: Print values to copy into .env
# ---------------------------------------------------------------------------
print("\n=== SUCCESS -- Copy these into your .env file ===\n")
print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
print(f"LINKEDIN_PERSON_URN={person_urn}")
print("\n=== DO NOT share these values publicly ===")
print("Token is valid for 60 days. Run this script again when it expires.\n")