# auth/facebook/diagnose_token.py
# Diagnoses your Facebook token to check what permissions it actually has.
# Run from project root:
#   python auth/facebook/diagnose_token.py

import os
import sys
import json
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

TOKEN   = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "").strip()
APP_ID  = os.getenv("FACEBOOK_APP_ID", "").strip()

print("\n=== Facebook Token Diagnostics ===\n")
print(f"Token:   {TOKEN[:15]}...")
print(f"Page ID: {PAGE_ID}")
print(f"App ID:  {APP_ID}")

# ---------------------------------------------------------------------------
# Check 1: Who does the token belong to
# ---------------------------------------------------------------------------
print("\n--- Check 1: Token identity ---")
r1 = requests.get(
    "https://graph.facebook.com/v25.0/me",
    params={
        "access_token": TOKEN,
        "fields":        "id,name",
    },
    timeout=10,
)
print(json.dumps(r1.json(), indent=2))

# ---------------------------------------------------------------------------
# Check 2: What permissions the token actually has
# ---------------------------------------------------------------------------
print("\n--- Check 2: Token permissions ---")
r2 = requests.get(
    "https://graph.facebook.com/v25.0/me/permissions",
    params={"access_token": TOKEN},
    timeout=10,
)
data = r2.json()
if "data" in data:
    print("Permission                    Status")
    print("-" * 45)
    for perm in data["data"]:
        status = perm.get("status", "unknown")
        name   = perm.get("permission", "unknown")
        mark   = "GRANTED" if status == "granted" else "DECLINED"
        print(f"{name:<35} {mark}")
else:
    print(json.dumps(data, indent=2))

# ---------------------------------------------------------------------------
# Check 3: Can the token see the Page
# ---------------------------------------------------------------------------
print(f"\n--- Check 3: Page access for {PAGE_ID} ---")
r3 = requests.get(
    f"https://graph.facebook.com/v25.0/{PAGE_ID}",
    params={
        "access_token": TOKEN,
        "fields":        "id,name,fan_count",
    },
    timeout=10,
)
print(json.dumps(r3.json(), indent=2))

# ---------------------------------------------------------------------------
# Check 4: Try posting a draft (does not actually post)
# ---------------------------------------------------------------------------
print("\n--- Check 4: Test post permission (unpublished draft) ---")
r4 = requests.post(
    f"https://graph.facebook.com/v25.0/{PAGE_ID}/feed",
    params={"access_token": TOKEN},
    json={
        "message":     "Diagnostic test -- this is unpublished",
        "published":   False,
    },
    timeout=10,
)
result = r4.json()
if "id" in result:
    print("Post permission: CONFIRMED (draft created successfully)")
    print(f"Draft ID: {result['id']} (not visible to public)")
else:
    print("Post permission: FAILED")
    print(json.dumps(result, indent=2))

print("\n=== Diagnostics Complete ===\n")