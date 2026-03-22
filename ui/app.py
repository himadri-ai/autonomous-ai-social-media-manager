# ui/app.py
# Streamlit UI for Autonomous Social Media Agent

import base64
import html as _html
import json
import os
import sys
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.content_agent import generate_posts
from config.settings import POST_HISTORY_PATH, validate_settings
from publishers.facebook_publisher import post_to_facebook
from publishers.linkedin_publisher import post_to_linkedin

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Social Media Manager",
    page_icon="📣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main .block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 2rem;
    max-width: 1400px;
}

[data-testid="stSidebar"] { background: #0f1117; border-right: 1px solid #1e2130; }
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

.section-header {
    font-size: 11px; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #6b7280;
    margin-bottom: 0.4rem; margin-top: 0.8rem;
}
h2 { margin-top: 0 !important; margin-bottom: 0.2rem !important; }

.platform-badge {
    display:inline-flex; align-items:center; gap:6px;
    padding:3px 10px; border-radius:20px;
    font-size:12px; font-weight:500; margin-right:6px;
}
.badge-success { background:#d1fae5; color:#065f46; border:1px solid #065f46; }
.badge-error   { background:#fee2e2; color:#991b1b; border:1px solid #991b1b; }

.char-count { font-size:11px; color:#9ca3af; text-align:right; margin-top:2px; }
.char-warn  { font-size:11px; color:#f59e0b; text-align:right; margin-top:2px; }
.char-over  { font-size:11px; color:#ef4444; text-align:right; margin-top:2px; }

.history-row {
    background:#f9fafb; border:1px solid #e5e7eb;
    border-radius:6px; padding:12px 16px; margin-bottom:8px;
}

/* ── LinkedIn native preview ── */
.li-card {
    background:#fff;
    border:1px solid #e0e0e0;
    border-radius:8px;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    overflow:hidden;
    box-shadow:0 1px 3px rgba(0,0,0,.08);
}
.li-top { padding:12px 16px 0; }
.li-header { display:flex; align-items:flex-start; gap:10px; margin-bottom:10px; }
.li-avatar {
    width:48px; height:48px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,#0a66c2,#00a0dc);
    display:flex; align-items:center; justify-content:center;
    color:#fff; font-weight:700; font-size:20px;
}
.li-name  { font-weight:600; font-size:14px; color:#000000e6; line-height:1.4; }
.li-title { font-size:12px; color:#00000099; line-height:1.4; }
.li-time  { font-size:12px; color:#00000099; display:flex; align-items:center; gap:4px; }
.li-follow {
    margin-left:auto; color:#0a66c2; font-size:14px; font-weight:600;
    display:flex; align-items:center; gap:4px; cursor:pointer; padding-top:2px;
}
.li-body {
    font-size:14px; line-height:1.6; color:#000000e6;
    padding:0 16px 12px;
    white-space:pre-wrap; word-break:break-word;
}
.li-img { width:100%; display:block; }
.li-reactions {
    padding:6px 16px 2px;
    font-size:12px; color:#00000099;
    display:flex; align-items:center; gap:4px;
    border-bottom:1px solid #e0e0e0;
}
.li-reaction-icons { display:flex; margin-right:4px; }
.li-actions {
    display:flex; padding:4px 8px;
}
.li-action-btn {
    flex:1; display:flex; align-items:center; justify-content:center; gap:6px;
    padding:10px 4px; border-radius:4px; cursor:pointer;
    font-size:13px; font-weight:600; color:#00000099;
}
.li-action-btn:hover { background:#f3f2ef; }

/* ── Facebook native preview ── */
.fb-card {
    background:#fff;
    border:1px solid #dddfe2;
    border-radius:8px;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    overflow:hidden;
    box-shadow:0 1px 3px rgba(0,0,0,.08);
}
.fb-top { padding:12px 16px 8px; }
.fb-header { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.fb-avatar {
    width:40px; height:40px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,#1877f2,#42a5f5);
    display:flex; align-items:center; justify-content:center;
    color:#fff; font-weight:700; font-size:17px;
}
.fb-name     { font-weight:600; font-size:15px; color:#050505; line-height:1.3; }
.fb-meta     { font-size:12px; color:#65676b; display:flex; align-items:center; gap:4px; }
.fb-body     {
    font-size:15px; line-height:1.5; color:#050505;
    padding:0 16px 12px;
    white-space:pre-wrap; word-break:break-word;
}
.fb-img      { width:100%; display:block; }
.fb-counts   {
    padding:8px 16px 4px;
    font-size:13px; color:#65676b;
    display:flex; justify-content:space-between; align-items:center;
    border-bottom:1px solid #e4e6eb;
}
.fb-like-row { display:flex; align-items:center; gap:4px; }
.fb-actions  { display:flex; padding:4px 8px; }
.fb-action-btn {
    flex:1; display:flex; align-items:center; justify-content:center; gap:6px;
    padding:8px 4px; border-radius:6px; cursor:pointer;
    font-size:14px; font-weight:600; color:#65676b;
}
.fb-action-btn:hover { background:#f0f2f5; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SVG icon constants -- native platform icons
# ---------------------------------------------------------------------------

# LinkedIn icons (official color: #666)
LI_ICON_LIKE = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00000099" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/></svg>"""
LI_ICON_COMMENT = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00000099" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""
LI_ICON_REPOST = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00000099" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 2 4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>"""
LI_ICON_SEND = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00000099" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>"""

# LinkedIn reaction dots
LI_REACT_LIKE  = """<svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="9" fill="#378fe9"/><path d="M5 9.5c0-.83.67-1.5 1.5-1.5h.09A2.5 2.5 0 0 1 9 6.5a2.5 2.5 0 0 1 2.41 1.5H12a1.5 1.5 0 0 1 0 3H6.5A1.5 1.5 0 0 1 5 9.5z" fill="#fff"/></svg>"""
LI_REACT_LOVE  = """<svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="9" fill="#df704d"/><path d="M9 13s-4-2.5-4-5.5a2.5 2.5 0 0 1 4-2 2.5 2.5 0 0 1 4 2C13 10.5 9 13 9 13z" fill="#fff"/></svg>"""
LI_REACT_INSIGHTFUL = """<svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="9" fill="#f5bb5c"/><path d="M9 5a2 2 0 0 0-2 2c0 1.1.9 2 2 2s2-.9 2-2a2 2 0 0 0-2-2zm-1 5v3h2v-3H8z" fill="#fff"/></svg>"""

# Facebook icons
FB_ICON_LIKE = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#65676b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/></svg>"""
FB_ICON_COMMENT = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#65676b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""
FB_ICON_SHARE = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#65676b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>"""

# Facebook reaction emoji circle
FB_REACT_LIKE  = """<svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="9" fill="#1877f2"/><path d="M5 9.5c0-.83.67-1.5 1.5-1.5h.09A2.5 2.5 0 0 1 9 6.5a2.5 2.5 0 0 1 2.41 1.5H12a1.5 1.5 0 0 1 0 3H6.5A1.5 1.5 0 0 1 5 9.5z" fill="#fff"/></svg>"""
FB_REACT_HEART = """<svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="9" fill="#f33e58"/><path d="M9 13s-4-2.5-4-5.5a2.5 2.5 0 0 1 4-2 2.5 2.5 0 0 1 4 2C13 10.5 9 13 9 13z" fill="#fff"/></svg>"""
FB_REACT_HAHA  = """<svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="9" fill="#f7b125"/><text x="9" y="13" text-anchor="middle" font-size="9" fill="#fff">😄</text></svg>"""

# Globe icon for both
GLOBE_ICON = """<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#65676b" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_history() -> list:
    if not os.path.exists(POST_HISTORY_PATH):
        return []
    try:
        with open(POST_HISTORY_PATH, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except Exception:
        return []


def save_history(record: dict) -> None:
    history = load_history()
    history.insert(0, record)
    with open(POST_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def char_css(count: int, limit: int) -> str:
    ratio = count / limit
    if ratio >= 1.0:
        return "char-over"
    if ratio >= 0.85:
        return "char-warn"
    return "char-count"


def image_to_base64(file_obj) -> str:
    file_obj.seek(0)
    data = file_obj.read()
    b64  = base64.b64encode(data).decode()
    return f"data:image/jpeg;base64,{b64}"


def linkedin_preview(safe_text: str, img_html: str) -> str:
    return f"""
<div class="li-card">
  <div class="li-top">
    <div class="li-header">
      <div class="li-avatar">H</div>
      <div style="flex:1">
        <div class="li-name">Himadri Sen</div>
        <div class="li-title">AI Trainer &amp; Consultant | Helping teams adopt AI</div>
        <div class="li-time">{GLOBE_ICON} Just now</div>
      </div>
      <div class="li-follow">+ Follow</div>
    </div>
  </div>
  <div class="li-body">{safe_text}</div>
  {img_html}
  <div class="li-reactions">
    <div class="li-reaction-icons">
      {LI_REACT_LIKE}{LI_REACT_LOVE}{LI_REACT_INSIGHTFUL}
    </div>
    <span>Be the first to react</span>
  </div>
  <div class="li-actions">
    <div class="li-action-btn">{LI_ICON_LIKE} Like</div>
    <div class="li-action-btn">{LI_ICON_COMMENT} Comment</div>
    <div class="li-action-btn">{LI_ICON_REPOST} Repost</div>
    <div class="li-action-btn">{LI_ICON_SEND} Send</div>
  </div>
</div>"""


def facebook_preview(safe_text: str, img_html: str) -> str:
    return f"""
<div class="fb-card">
  <div class="fb-top">
    <div class="fb-header">
      <div class="fb-avatar">H</div>
      <div>
        <div class="fb-name">Himadri Sen</div>
        <div class="fb-meta">Just now &nbsp;·&nbsp; {GLOBE_ICON}</div>
      </div>
    </div>
  </div>
  <div class="fb-body">{safe_text}</div>
  {img_html}
  <div class="fb-counts">
    <div class="fb-like-row">
      {FB_REACT_LIKE}{FB_REACT_HEART}{FB_REACT_HAHA}
      <span style="margin-left:4px;">Be the first to react</span>
    </div>
    <span>0 comments · 0 shares</span>
  </div>
  <div class="fb-actions">
    <div class="fb-action-btn">{FB_ICON_LIKE} Like</div>
    <div class="fb-action-btn">{FB_ICON_COMMENT} Comment</div>
    <div class="fb-action-btn">{FB_ICON_SHARE} Share</div>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## AI Social Media Manager")
    st.markdown("---")
    page  = st.radio("Navigation", ["Create Post", "Post History"], label_visibility="collapsed")
    creds = validate_settings()

    st.markdown("---")
    st.markdown('<p class="section-header">Platform Status</p>', unsafe_allow_html=True)
    st.markdown(f"{'🟢' if creds['linkedin'] else '🔴'} **LinkedIn** — {'Connected' if creds['linkedin'] else 'Not configured'}")
    st.markdown(f"{'🟢' if creds['facebook'] else '🔴'} **Facebook** — {'Connected' if creds['facebook'] else 'Not configured'}")
    if not creds["groq"]:
        st.warning("Groq API key missing in .env")

    st.markdown("---")
    st.caption("v1.0 · Local Mode · Open Source")


# ===========================================================================
# PAGE 1: Create Post
# ===========================================================================
if page == "Create Post":

    st.markdown("## Create Post")
    st.markdown("Generate AI copy, review it, then publish to your connected platforms.")

    # AI Generator panel
    with st.expander("AI Content Generator", expanded=not st.session_state.get("generated", False)):
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            keywords = st.text_input("Topic Keywords", placeholder="e.g. AI consulting, HR automation")
        with c2:
            tone = st.selectbox("Tone", ["Educational", "Motivational", "Promotional", "Storytelling", "Thought Leadership"])
        with c3:
            audience = st.text_input("Target Audience", placeholder="e.g. HR managers, founders")

        if st.button("Generate Posts", type="primary", width='stretch'):
            if not keywords.strip():
                st.error("Please enter at least one topic keyword.")
            elif not creds["groq"]:
                st.error("Groq API key not configured in .env")
            else:
                with st.spinner("Generating your posts..."):
                    result = generate_posts(keywords, tone, audience)
                if result["error"]:
                    st.error(f"Generation failed: {result['error']}")
                else:
                    st.session_state["long_post"]  = result["long_post"]
                    st.session_state["short_post"] = result["short_post"]
                    st.session_state["generated"]  = True
                    st.session_state["keywords"]   = keywords
                    st.session_state["tone"]       = tone
                    st.session_state["audience"]   = audience
                    st.rerun()

    # Two column layout
    if st.session_state.get("generated", False):

        col_left, col_right = st.columns([1, 1], gap="large")

        # LEFT: Compose
        with col_left:
            st.markdown('<p class="section-header">Compose</p>', unsafe_allow_html=True)

            st.markdown("**Post to**")
            pc1, pc2 = st.columns(2)
            with pc1:
                use_linkedin = st.checkbox("LinkedIn", value=creds["linkedin"], disabled=not creds["linkedin"])
            with pc2:
                use_facebook = st.checkbox("Facebook", value=creds["facebook"], disabled=not creds["facebook"])

            if not creds["linkedin"] and not creds["facebook"]:
                st.warning("No platforms configured. Add credentials to .env to enable posting.")

            st.markdown("---")

            post_variant = st.radio(
                "Post variant",
                ["Long form (LinkedIn / Facebook)", "Short form (Twitter style)"],
                horizontal=True,
                key="post_variant",
            )

            is_long    = post_variant == "Long form (LinkedIn / Facebook)"
            char_limit = 1000 if is_long else 150
            default    = st.session_state.get("long_post" if is_long else "short_post", "")

            edited_text = st.text_area(
                "Post text",
                value=default,
                height=220,
                max_chars=char_limit,
                label_visibility="collapsed",
                key=f"editor_{'long' if is_long else 'short'}",
            )

            count = len(edited_text)
            st.markdown(
                f'<p class="{char_css(count, char_limit)}">{count} / {char_limit} characters</p>',
                unsafe_allow_html=True,
            )

            # Updated media upload label
            st.markdown(
                "**Attach Image or Video (Max 200 MB)**  \n"
                "<small style='color:#9ca3af;'>JPG, JPEG, PNG, MP4, MOV</small>",
                unsafe_allow_html=True,
            )
            uploaded_file = st.file_uploader(
                "Upload",
                type=["jpg", "jpeg", "png", "mp4", "mov"],
                label_visibility="collapsed",
            )
            if uploaded_file:
                if uploaded_file.type.startswith("image"):
                    st.image(uploaded_file, width='stretch')
                else:
                    st.video(uploaded_file)

            st.markdown("---")

            post_clicked = st.button(
                "Post Now",
                type="primary",
                width='stretch',
                disabled=(not use_linkedin and not use_facebook),
            )

            if post_clicked:
                image_bytes = None
                if uploaded_file and uploaded_file.type.startswith("image"):
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()

                results   = {}
                platforms = []
                if use_linkedin:
                    platforms.append("LinkedIn")
                if use_facebook:
                    platforms.append("Facebook")

                with st.spinner(f"Posting to {', '.join(platforms)}..."):
                    if use_linkedin:
                        results["LinkedIn"] = post_to_linkedin(edited_text, image_bytes)
                    if use_facebook:
                        results["Facebook"] = post_to_facebook(edited_text, image_bytes)

                all_success = all(r["success"] for r in results.values())
                for platform, res in results.items():
                    if res["success"]:
                        st.success(f"{platform}: Posted successfully (ID: {res['post_id']})")
                    else:
                        st.error(f"{platform}: Failed — {res['error']}")

                save_history({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "keywords":  st.session_state.get("keywords", ""),
                    "tone":      st.session_state.get("tone", ""),
                    "text":      edited_text[:120] + "..." if len(edited_text) > 120 else edited_text,
                    "platforms": platforms,
                    "status":    "success" if all_success else "partial",
                    "results":   {p: r["success"] for p, r in results.items()},
                })

        # RIGHT: Live Preview
        with col_right:
            st.markdown('<p class="section-header">Preview</p>', unsafe_allow_html=True)
            preview_platform = st.radio("Preview as", ["LinkedIn", "Facebook"], horizontal=True)

            # Image for preview
            img_html_li = ""
            img_html_fb = ""
            if uploaded_file and uploaded_file.type.startswith("image"):
                img_src     = image_to_base64(uploaded_file)
                img_html_li = f'<img class="li-img" src="{img_src}" alt="post image"/>'
                img_html_fb = f'<img class="fb-img" src="{img_src}" alt="post image"/>'

            # Escape and preserve line breaks
            raw  = edited_text if edited_text else "Your post will appear here..."
            safe = _html.escape(raw).replace("\n", "<br>")

            if preview_platform == "LinkedIn":
                st.markdown(linkedin_preview(safe, img_html_li), unsafe_allow_html=True)
            else:
                st.markdown(facebook_preview(safe, img_html_fb), unsafe_allow_html=True)

    else:
        st.info("Fill in the AI Content Generator above and click Generate Posts to get started.")


# ===========================================================================
# PAGE 2: Post History
# ===========================================================================
elif page == "Post History":

    st.markdown("## Post History")
    history = load_history()

    if not history:
        st.info("No posts yet. Go to Create Post to publish your first post.")
    else:
        st.markdown(f"**{len(history)} post(s) recorded**")
        st.markdown("---")

        for record in history:
            status       = record.get("status", "unknown")
            status_badge = "badge-success" if status == "success" else "badge-error"
            status_label = "Published" if status == "success" else "Partial / Failed"

            results_html = ""
            for platform, success in record.get("results", {}).items():
                icon = "✓" if success else "✗"
                cls  = "badge-success" if success else "badge-error"
                results_html += f'<span class="platform-badge {cls}">{icon} {platform}</span>'

            st.markdown(f"""
<div class="history-row">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div>
      <strong>{record.get('timestamp','')}</strong>
      &nbsp;&nbsp;
      <span style="color:#6b7280;font-size:13px;">{record.get('tone','')} · {record.get('keywords','')}</span>
    </div>
    <span class="platform-badge {status_badge}">{status_label}</span>
  </div>
  <div style="margin-top:8px;font-size:14px;color:#374151;">{record.get('text','')}</div>
  <div style="margin-top:8px;">{results_html}</div>
</div>""", unsafe_allow_html=True)

        if st.button("Clear History", type="secondary"):
            with open(POST_HISTORY_PATH, "w") as f:
                json.dump([], f)
            st.rerun()