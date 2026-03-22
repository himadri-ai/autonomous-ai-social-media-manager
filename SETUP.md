# SETUP.md - Credential Configuration Guide

This guide walks you through getting every API key and token needed to run the AI Social Media Manager. Each section takes 5–10 minutes.

---

## What You Need

| Credential | Platform | Used For |
|---|---|---|
| `GROQ_API_KEY` | Groq Console | AI post generation (free) |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn Developer | Posting to LinkedIn |
| `LINKEDIN_PERSON_URN` | LinkedIn API | Identifying your LinkedIn account |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Meta Developer | Posting to your Facebook Page |
| `FACEBOOK_PAGE_ID` | Facebook | Identifying your Facebook Page |

---

## Step 1: Groq API Key (5 minutes - Free)

Groq provides free access to Llama 3.3 70B with generous rate limits.

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Click **API Keys** in the left sidebar
4. Click **Create API Key**
5. Copy the key (starts with `gsk_`)

Add to `.env`:
```
GROQ_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.3-70b-versatile
```

---

## Step 2: LinkedIn Credentials (10 minutes)

LinkedIn requires a Developer App to post via API.

### 2a. Create a LinkedIn Developer App

1. Go to [developer.linkedin.com/apps](https://developer.linkedin.com/apps)
2. Click **Create App**
3. Fill in:
   - App Name: `AI Social Media Manager`
   - LinkedIn Page: select your personal profile or company page
   - App Logo: upload any image
4. Click **Create App**

### 2b. Enable the right API products

1. In your app dashboard click the **Products** tab
2. Request access to **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**
3. Both are approved instantly for personal use

### 2c. Get your Access Token

1. Click the **Auth** tab in your app dashboard
2. Note your **Client ID** and **Client Secret**
3. Go to [linkedin.com/developers/tools/oauth/token-generator](https://www.linkedin.com/developers/tools/oauth/token-generator)
4. Select your app
5. Check these scopes: `openid`, `profile`, `w_member_social`
6. Click **Request access token**
7. Approve the OAuth prompt in your browser
8. Copy the **Access Token** (valid for 60 days)

### 2d. Get your Person URN

With your access token, run this in your terminal (replace `YOUR_TOKEN`):

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.linkedin.com/v2/userinfo
```

Look for the `sub` field in the response. Your Person URN is:
```
urn:li:person:SUB_VALUE_HERE
```

Add to `.env`:
```
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_PERSON_URN=urn:li:person:your_sub_here
```

---

## Step 3: Facebook Page Credentials (10 minutes)

Facebook API only works with **Facebook Pages**, not personal profiles. You need a Page to use this feature.

### 3a. Create a Facebook Page (if you do not have one)

1. Go to [facebook.com/pages/create](https://www.facebook.com/pages/create)
2. Choose **Business or Brand**
3. Give it a name and category
4. You do not need to publish it publicly to use the API

### 3b. Get your Page ID

1. Go to your Facebook Page
2. Click **About** in the left sidebar
3. Scroll down to find **Page ID** (a long number like `123456789012345`)

### 3c. Create a Meta Developer App

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps)
2. Click **Create App**
3. Select **Other** then **Business**
4. Give it a name and click **Create App**

### 3d. Get a Page Access Token

1. In your Meta Developer App go to **Tools > Graph API Explorer**
2. Select your app from the dropdown
3. Click **Generate Access Token** and log in with Facebook
4. In the permissions list check: `pages_manage_posts`, `pages_read_engagement`
5. Click **Generate Access Token** and approve
6. In the left panel change the endpoint to:
   ```
   GET /me/accounts
   ```
7. Click **Submit**
8. Find your Page in the response and copy its `access_token` value

Add to `.env`:
```
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

---

## Final .env File

Your completed `.env` should look like this:

```
# LLM
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
LLM_MODEL=llama-3.3-70b-versatile

# LinkedIn
LINKEDIN_ACCESS_TOKEN=AQxxxxxxxxxxxxxxxxxxxxxx
LINKEDIN_PERSON_URN=urn:li:person:xxxxxxxxx

# Facebook
FACEBOOK_PAGE_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxx
FACEBOOK_PAGE_ID=123456789012345
```

---

## Verify Your Setup

Run this in your terminal (with venv active):

```bash
python -c "from config.settings import validate_settings; print(validate_settings())"
```

Expected output when everything is configured:
```
{'groq': True, 'linkedin': True, 'facebook': True}
```

---

## Token Expiry Notes

| Token | Expiry | How to Refresh |
|---|---|---|
| Groq API Key | Never | Regenerate in console if compromised |
| LinkedIn Access Token | 60 days | Repeat Step 2c |
| Facebook Page Token | 60 days (short) or never (long-lived) | Use Token Debugger to extend |

To convert a Facebook short-lived token to a long-lived one, use the
[Meta Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/).

---

## Common Errors

**`{'groq': False}`** — Your Groq key is wrong or still a placeholder. Double check it starts with `gsk_`.

**`LinkedIn: HTTP 401`** — Access token expired (60-day limit). Regenerate via Step 2c.

**`Facebook: Invalid OAuth access token`** — Page token expired. Regenerate via Step 3d.

**`Facebook: (#200) The user hasn't authorized the application`** — You need to re-add `pages_manage_posts` permission in Graph API Explorer.
