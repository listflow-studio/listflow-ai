import os
import json
import tempfile
import urllib.parse
from datetime import datetime
from PIL import Image
import streamlit as st
import requests
from google import genai
from google.genai import types

# -------------------------------------------------------------
# Streamlit Page Configuration & White-Label CSS
# -------------------------------------------------------------
st.set_page_config(
    page_title="ListFlow AI | Real Estate Marketing Studio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# White-label styling
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    .stDecoration {display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: -webkit-sticky; position: sticky;}
    div[data-testid="stDecoration"] {display: none;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .guide-box {
        background-color: #F8FAFC;
        border-left: 4px solid #2563EB;
        padding: 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        line-height: 1.6;
    }
    .paywall-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin: 20px 0;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -------------------------------------------------------------
# Credit & Lead Management Engine
# -------------------------------------------------------------
def get_webhook_url():
    if "LEADS_WEBHOOK_URL" in st.secrets:
        return st.secrets["LEADS_WEBHOOK_URL"]
    return os.environ.get("LEADS_WEBHOOK_URL")

def check_user_credits(phone):
    """Queries the Google Sheet backend for remaining trial credits."""
    webhook_url = get_webhook_url()
    if not webhook_url or not phone.strip():
        return 2, True
    try:
        resp = requests.post(webhook_url, json={"action": "check", "phone": phone}, timeout=4)
        data = resp.json()
        if data.get("status") == "success":
            return data.get("credits_left", 2), data.get("is_allowed", True)
    except Exception:
        pass
    return 2, True

def log_and_deduct_credit(name, phone, ig, email, rera):
    """Logs the lead row and decrements available credits."""
    lead_entry = {
        "action": "log",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name.strip(),
        "phone": phone.strip(),
        "email": email.strip(),
        "instagram": ig.strip() if ig else "",
        "rera": rera.strip() if rera else ""
    }
    
    webhook_url = get_webhook_url()
    if webhook_url:
        try:
            resp = requests.post(webhook_url, json=lead_entry, timeout=5)
            data = resp.json()
            return data.get("is_allowed", True), data.get("credits_left", 0)
        except Exception:
            pass
    return True, 1

# -------------------------------------------------------------
# Gemini Client Initialization
# -------------------------------------------------------------
def get_gemini_client():
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    elif os.environ.get("GEMINI_API_KEY"):
        api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ Gemini API Key not configured. Please add `GEMINI_API_KEY` to Streamlit Secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# -------------------------------------------------------------
# Sidebar: Agent Profile, Credit Meter & Reset
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&auto=format&fit=crop&q=80", use_container_width=True)
    st.title("🏢 ListFlow AI")
    st.caption("AI-Powered Multi-Channel Real Estate Studio")
    
    st.markdown("---")
    st.subheader("👤 Agent / Builder Profile")
    st.caption("Required to brand your launch materials and activate trial credits:")
    
    agent_name = st.text_input("Name / Agency / Builder Name *", placeholder="e.g., Apex Realty / Rajesh Kumar", key="ag_name")
    agent_phone = st.text_input("WhatsApp Number (10 Digits) *", placeholder="e.g., 9884012345", key="ag_phone")
    agent_email = st.text_input("Email ID *", placeholder="e.g., contact@apexrealty.com", key="ag_email")
    agent_ig = st.text_input("Instagram Handle (Optional)", placeholder="e.g., @apexrealty_official", key="ag_ig")
    agent_rera = st.text_input("RERA / License ID (Optional)", placeholder="e.g., TN/AGENT/2026/00123", key="ag_rera")
    
    # Credit Badge Indicator
    clean_digits = "".join(filter(str.isdigit, agent_phone))
    if len(clean_digits) >= 10:
        credits_left, is_allowed = check_user_credits(clean_digits)
        if is_allowed:
            st.success(f"⚡ **Free Trial Active:** {credits_left} generation(s) left")
        else:
            st.error("🔒 **Trial Expired:** 0 credits remaining")
    
    st.markdown("---")
    if st.button("🔄 Reset Studio", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.subheader("📩 Feedback & Inquiries")
    support_email = "neyora.admin@gmail.com"
    email_subject = "ListFlow%20AI%20Inquiry%20%26%20Feedback"
    st.markdown(f"📧 **Email Desk:** [{support_email}](mailto:{support_email}?subject={email_subject})")
    st.caption("Replies within 24–48 hours.")
    st.caption("Powered by Neyora Studios • Version 1.0.0")

# -------------------------------------------------------------
# Main Application Interface
# -------------------------------------------------------------
st.markdown('<div class="main-title">ListFlow AI — Real Estate Launch Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Turn property specs, photos, and walkthrough videos into high-converting 6-channel marketing campaigns.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 0.9], gap="medium")

with col1:
    st.subheader("📝 Property Specifications")
    
    prop_title = st.text_input("Property Headline / Name", placeholder="e.g., Ultra-Luxury 3 BHK Penthouse in Anna Nagar", key="p_title")
    
    c1, c2 = st.columns(2)
    with c1:
        prop_location = st.text_input("Location / Neighborhood *", placeholder="e.g., Anna Nagar West, Chennai", key="p_loc")
        prop_price = st.text_input("Price / Price Range *", placeholder="e.g., ₹1.85 Cr (Negotiable)", key="p_price")
    with c2:
        prop_type = st.selectbox("Property Type", ["Residential Apartment", "Independent Villa", "Plot / Land", "Commercial Space", "Penthouse", "Studio Apartment"], key="p_type")
        prop_size = st.text_input("Built-up Area / Carpet Area", placeholder="e.g., 1,850 sq.ft (Carpet)", key="p_size")
        
    prop_specs = st.text_area("Key Features & Amenities *", placeholder="e.g., 3 Bedrooms, 3 Bathrooms, 2 Balconies, East Facing, Modular Kitchen, 2 Covered Car Parks, Swimming Pool, Clubhouse, 24/7 Security.", height=110, key="p_specs")

with col2:
    st.subheader("🎯 Campaign Strategy & Visuals")
    
    campaign_angle = st.selectbox(
        "Conversion Angle & Tone",
        [
            "🔥 HOT Deal / High Urgency (Fast Closing)",
            "💎 Luxury & Prestige (High-End Exclusive)",
            "📈 High-ROI Investor Focus (High Rental Yields & Appreciation)",
            "⏳ Urgent Distress Sale (Priced to Sell Fast)",
            "🌍 NRI / Global Investor Focus (Turnkey Asset Management)"
        ],
        key="c_angle"
    )
    
    target_language = st.selectbox(
        "Campaign Language / Tone",
        [
            "English",
            "Tamil (தமிழ்)",
            "Hindi (हिन्दी)",
            "Telugu (తెలుగు)",
            "Kannada (ಕನ್ನಡ)",
            "Malayalam (മലയാളം)",
            "Tanglish (Tamil + English Hybrid)",
            "Hinglish (Hindi + English Hybrid)"
        ],
        key="t_lang"
    )
    
    media_tab1, media_tab2 = st.tabs(["📸 Upload Property Photos (Multiple)", "🎥 Upload Video Walkthrough"])
    
    uploaded_photos = []
    uploaded_video = None
    
    with media_tab1:
        uploaded_photos = st.file_uploader(
            "Select and upload multiple property images (Living Room, Kitchen, Bedrooms, Exterior):", 
            type=["jpg", "jpeg", "png", "webp"], 
            accept_multiple_files=True,
            key="img_up"
        )
        if uploaded_photos:
            st.caption(f"📸 **{len(uploaded_photos)} photo(s) selected** for AI vision analysis")
            grid_cols = st.columns(min(len(uploaded_photos), 4))
            for idx, photo in enumerate(uploaded_photos[:4]):
                with grid_cols[idx]:
                    st.image(Image.open(photo), use_container_width=True)
            if len(uploaded_photos) > 4:
                st.caption(f"+ {len(uploaded_photos) - 4} more photos queued for analysis")
            
    with media_tab2:
        uploaded_video = st.file_uploader("Upload Walkthrough Video Clip", type=["mp4", "mov", "avi"], key="vid_up")
        if uploaded_video:
            st.video(uploaded_video)

# -------------------------------------------------------------
# Campaign Generation Engine (With Credit Enforcement)
# -------------------------------------------------------------
st.markdown("---")

generate_btn = st.button("🚀 Generate Multi-Channel Campaign", type="primary", use_container_width=True)

if generate_btn:
    clean_digits = "".join(filter(str.isdigit, agent_phone))
    
    if not agent_name.strip() or len(clean_digits) < 10 or not agent_email.strip():
        st.error("⚠️ Please complete the required **Agent Profile** fields in the sidebar (Name, 10-digit WhatsApp, and Email).")
    elif not prop_location.strip() or not prop_price.strip() or not prop_specs.strip():
        st.warning("⚠️ Please provide at least the Location, Price, and Key Features before generating.")
    else:
        # Pre-check credit limit before API execution
        credits_left, is_allowed = check_user_credits(clean_digits)
        
        if not is_allowed:
            # Paywall Card for exhausted trial accounts
            st.markdown(f"""
            <div class="paywall-card">
                <h3 style="color:#60A5FA; margin-top:0;">🔒 You have used your 2 free campaign credits!</h3>
                <p>We hope ListFlow AI helped you market your listings faster. Upgrade to continue generating unlimited, high-converting launch kits.</p>
                <hr style="border-color:#334155;">
                <p><strong>✨ Pro Plan Includes:</strong></p>
                <ul>
                    <li>Unlimited Multi-Channel Property Launches</li>
                    <li>30s Video Reel Scripts & Walkthrough Narratives</li>
                    <li>All 8 Regional Language Outputs (Tamil, Hindi, Telugu, etc.)</li>
                    <li>Direct WhatsApp & Social Media Posting Playbook</li>
                </ul>
                <p style="margin-top:15px;">👉 <strong>To activate your Pro account or buy credits, email us at:</strong> <a href="mailto:neyora.admin@gmail.com?subject=ListFlow%20Pro%20Upgrade%20Request%20-%20{clean_digits}" style="color:#38BDF8;">neyora.admin@gmail.com</a></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("✨ Analyzing property specs, visuals, and crafting your 6-channel campaign..."):
                
                clean_phone = clean_digits
                if not clean_phone.startswith("91") and len(clean_phone) == 10:
                    clean_phone = f"91{clean_phone}"
                
                wa_inquiry_msg = urllib.parse.quote(f"Hi {agent_name}, I am interested in the {prop_title or 'property'} at {prop_location} priced at {prop_price}. Please share full details.")
                wa_link = f"https://wa.me/{clean_phone}?text={wa_inquiry_msg}"

                prompt_text = f"""
You are an elite Real Estate Marketing Director and Growth Copywriter.
Generate a comprehensive, high-converting 6-channel marketing campaign package along with actionable social media posting instructions for the following property.

### PROPERTY DATA:
- Property Title: {prop_title}
- Location: {prop_location}
- Price: {prop_price}
- Property Type: {prop_type}
- Size: {prop_size}
- Specs & Amenities: {prop_specs}
- Conversion Strategy Angle: {campaign_angle}
- Output Language: {target_language} (Note: If a regional language like Tamil, Hindi, Telugu, Kannada, or Malayalam is selected, write the copy and posting instructions fluently in that native script).

### AGENT / BUILDER BRANDING:
- Agent/Agency/Builder: {agent_name}
- WhatsApp Number: {agent_phone}
- Instagram Handle: {agent_ig or '@realtor'}
- Email: {agent_email}
- RERA ID: {agent_rera or 'Available on Request'}
- Direct WhatsApp Inquiry Link: {wa_link}

### MULTIMODAL INSTRUCTION:
If property images or video clips are provided, analyze them carefully to extract architectural highlights, finishes, and lighting to naturally emphasize them in the copy and posting tips.

### OUTPUT JSON STRUCTURE:
Return strictly a valid JSON object with the following keys:
{{
  "whatsapp_blast": "Punchy, emoji-rich broadcast copy tailored for WhatsApp buyer groups with bold headlines, bulleted USPs, and clickable WhatsApp inquiry link.",
  "email_campaign": "Complete HTML/Markdown email newsletter with a catchy Subject Line, Preview Text, Engaging Body, Features, and Booking CTA.",
  "instagram_caption": "Engaging carousel/post caption with a compelling hook, lifestyle narrative, bullet points, IG tag, CTA to DM/WhatsApp, and 15 targeted hashtags.",
  "facebook_ad": "Conversational, community-focused Facebook ad copy with Primary Text, Catchy Headline, Link Description, and CTA.",
  "mls_portal_description": "Professional, compliance-checked listing overview suitable for 99acres, Housing.com, Magicbricks, or MLS.",
  "reel_script": "30-45 second short-form video reel script with timestamps, visual cues, and voiceover narration.",
  "posting_instructions": "Step-by-step posting playbook in the target language explaining how to pair uploaded photos/videos with this copy on WhatsApp, Instagram Carousel, Facebook, and Reels for maximum inquiries."
}}
Return ONLY raw, valid JSON.
"""

                try:
                    contents_payload = [prompt_text]
                    
                    if uploaded_photos:
                        for photo in uploaded_photos:
                            contents_payload.append(Image.open(photo))

                    if uploaded_video:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                            tmp_file.write(uploaded_video.read())
                            tmp_video_path = tmp_file.name
                        
                        video_upload_ref = client.files.upload(file=tmp_video_path)
                        contents_payload.append(video_upload_ref)

                    models_to_try = [
                        "gemini-3.6-flash",
                        "gemini-3.7-flash"
                    ]
                    
                    response = None
                    errors_log = []

                    for model_candidate in models_to_try:
                        try:
                            response = client.models.generate_content(
                                model=model_candidate,
                                contents=contents_payload,
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json"
                                )
                            )
                            if response and response.text:
                                break
                        except Exception as err:
                            errors_log.append(f"{model_candidate}: {str(err)}")
                            continue

                    if not response or not response.text:
                        raise Exception(" | ".join(errors_log))

                    result_data = json.loads(response.text)
                    st.session_state["campaign_result"] = result_data
                    st.session_state["wa_link"] = wa_link

                    # Log to Google Sheet and deduct 1 credit
                    allowed, remaining_after = log_and_deduct_credit(agent_name, agent_phone, agent_ig, agent_email, agent_rera)
                    st.success(f"🎉 Campaign generated! (You have {remaining_after} free generation(s) remaining)")

                except Exception as e:
                    st.error(f"Error generating campaign: {str(e)}")

# -------------------------------------------------------------
# Display Campaign Outputs
# -------------------------------------------------------------
if "campaign_result" in st.session_state:
    res = st.session_state["campaign_result"]
    wa_link = st.session_state.get("wa_link", "#")

    st.markdown("### 📦 Your Multi-Channel Campaign Kit")

    tab_guide, tab_wa, tab_email, tab_ig, tab_fb, tab_mls, tab_reel = st.tabs([
        "🚀 How to Post & Upload",
        "⚡ WhatsApp Broadcast",
        "✉️ Email Newsletter",
        "📸 Instagram & TikTok",
        "🌐 Facebook Post / Ad",
        "📋 MLS & Portal Listing",
        "🎬 30s Reel Script"
    ])

    with tab_guide:
        st.subheader("📖 Social Media Posting Playbook & Media Pairing Guide")
        st.markdown(f'<div class="guide-box">{res.get("posting_instructions", "Follow standard social media posting best practices.")}</div>', unsafe_allow_html=True)
        st.info("💡 **Tip:** Copy the ready-to-use text from the tabs on the right and pair it directly with your uploaded property photos or walkthrough video on each platform.")

    with tab_wa:
        st.subheader("WhatsApp Broadcast & Group Pitch")
        st.text_area("Ready-to-Copy WhatsApp Copy", value=res.get("whatsapp_blast", ""), height=260)
        st.markdown(f"👉 **Direct Buyer WhatsApp Link:** [{wa_link}]({wa_link})")

    with tab_email:
        st.subheader("Email Campaign / Newsletter Blast")
        st.text_area("Ready-to-Send Email Content", value=res.get("email_campaign", ""), height=320)

    with tab_ig:
        st.subheader("Instagram Post & Carousel Copy")
        st.text_area("Instagram Caption & Hashtags", value=res.get("instagram_caption", ""), height=280)

    with tab_fb:
        st.subheader("Facebook Post / Paid Ad Copy")
        st.text_area("Facebook Content", value=res.get("facebook_ad", ""), height=260)

    with tab_mls:
        st.subheader("MLS & Portal Description")
        st.text_area("Standard Portal Description", value=res.get("mls_portal_description", ""), height=280)

    with tab_reel:
        st.subheader("30–45s Video Reel / Shorts Walkthrough Script")
        st.text_area("Visual Pacing & Voiceover Script", value=res.get("reel_script", ""), height=300)

    # Export Full Campaign Bundle
    st.markdown("---")
    campaign_export_str = json.dumps(res, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download Full Campaign Bundle (.JSON)",
        data=campaign_export_str,
        file_name=f"ListFlow_Campaign_{prop_location.replace(' ', '_') or 'Export'}.json",
        mime="application/json",
        use_container_width=True
    )