import os
import json
import tempfile
import urllib.parse
from PIL import Image
import streamlit as st
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

# White-label styling: hide Streamlit default chrome, menu, footer & deploy badges
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
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
# Sidebar: Broker Profile, Reset Button & Support Drawer
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&auto=format&fit=crop&q=80", use_container_width=True)
    st.title("🏢 ListFlow AI")
    st.caption("AI-Powered Multi-Channel Real Estate Studio")
    
    if st.button("🔄 Reset Studio", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.subheader("👤 Agent / Broker Profile")
    st.caption("Enter your agency branding to auto-inject into listings:")
    agent_name = st.text_input("Agent / Agency Name", placeholder="e.g., Apex Realty Associates", key="ag_name")
    agent_phone = st.text_input("WhatsApp / Phone Number", placeholder="e.g., 9884012345", key="ag_phone")
    agent_email = st.text_input("Contact Email", placeholder="e.g., agent@apexrealty.com", key="ag_email")
    agent_rera = st.text_input("RERA / License ID (Optional)", placeholder="e.g., TN/AGENT/2026/00123", key="ag_rera")
    
    st.markdown("---")
    st.subheader("💬 Need Help or Have Feedback?")
    
    support_email = "neyora.admin@gmail.com"
    email_subject = "ListFlow%20AI%20Support%20%26%20Feedback"
    whatsapp_number = "919884395952"
    whatsapp_msg = "Hi%20Neyora%20Team%2C%20I%20have%20a%20question%20about%20ListFlow%20AI."
    
    st.markdown(
        f"""
        * 📧 **Email:** [{support_email}](mailto:{support_email}?subject={email_subject})
        * 💬 **WhatsApp:** [Chat with Neyora Support](https://wa.me/{whatsapp_number}?text={whatsapp_msg})
        """
    )
    
    with st.expander("📝 Submit Feedback Directly"):
        fb_note = st.text_area("Share your feature request or review:", height=80, key="fb_input")
        if fb_note.strip():
            encoded_fb = urllib.parse.quote(f"ListFlow AI User Feedback: {fb_note.strip()}")
            wa_fb_link = f"https://wa.me/{whatsapp_number}?text={encoded_fb}"
            st.markdown(f"[👉 Click to Send via WhatsApp]({wa_fb_link})", unsafe_allow_html=True)
            mail_fb_link = f"mailto:{support_email}?subject=ListFlow%20AI%20Feedback&body={encoded_fb}"
            st.markdown(f"[👉 Click to Send via Email]({mail_fb_link})", unsafe_allow_html=True)

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
        prop_location = st.text_input("Location / Neighborhood", placeholder="e.g., Anna Nagar West, Chennai", key="p_loc")
        prop_price = st.text_input("Price / Price Range", placeholder="e.g., ₹1.85 Cr (Negotiable)", key="p_price")
    with c2:
        prop_type = st.selectbox("Property Type", ["Residential Apartment", "Independent Villa", "Plot / Land", "Commercial Space", "Penthouse", "Studio Apartment"], key="p_type")
        prop_size = st.text_input("Built-up Area / Carpet Area", placeholder="e.g., 1,850 sq.ft (Carpet)", key="p_size")
        
    prop_specs = st.text_area("Key Features & Amenities", placeholder="e.g., 3 Bedrooms, 3 Bathrooms, 2 Balconies, East Facing, Modular Kitchen, 2 Covered Car Parks, Swimming Pool, Clubhouse, 24/7 Security.", height=110, key="p_specs")

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
    
    # Media Upload: Multi-Photo & Video Walkthrough Tabs
    media_tab1, media_tab2 = st.tabs(["📸 Upload Photos (Multi-Image)", "🎥 Upload Video Walkthrough"])
    
    uploaded_photos = []
    uploaded_video = None
    
    with media_tab1:
        uploaded_photos = st.file_uploader(
            "Upload Property Photos (Living Room, Kitchen, Balcony, Exterior)", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            key="img_up"
        )
        if uploaded_photos:
            st.caption(f"📸 {len(uploaded_photos)} photo(s) ready for multimodal AI analysis")
            grid_cols = st.columns(min(len(uploaded_photos), 4))
            for idx, photo in enumerate(uploaded_photos[:4]):
                with grid_cols[idx]:
                    st.image(Image.open(photo), use_container_width=True)
            if len(uploaded_photos) > 4:
                st.caption(f"+ {len(uploaded_photos) - 4} more photos queued for AI processing")
            
    with media_tab2:
        uploaded_video = st.file_uploader("Upload Walkthrough Video Clip", type=["mp4", "mov", "avi"], key="vid_up")
        if uploaded_video:
            st.video(uploaded_video)

# -------------------------------------------------------------
# Campaign Generation Engine
# -------------------------------------------------------------
st.markdown("---")

generate_btn = st.button("🚀 Generate Multi-Channel Campaign", type="primary", use_container_width=True)

if generate_btn:
    if not prop_location or not prop_price or not prop_specs:
        st.warning("⚠️ Please provide at least the Location, Price, and Key Features before generating.")
    else:
        with st.spinner("✨ Gemini is analyzing your property specs, photos & videos, and crafting your 6-channel campaign..."):
            
            clean_phone = "".join(filter(str.isdigit, agent_phone or "919884395952"))
            if not clean_phone.startswith("91") and len(clean_phone) == 10:
                clean_phone = f"91{clean_phone}"
            
            display_agent = agent_name if agent_name.strip() else "Direct Sales Desk"
            wa_inquiry_msg = urllib.parse.quote(f"Hi {display_agent}, I am interested in the {prop_title or 'property'} at {prop_location} priced at {prop_price}. Please share full details.")
            wa_link = f"https://wa.me/{clean_phone}?text={wa_inquiry_msg}"

            prompt_text = f"""
You are an elite Real Estate Copywriter and Growth Marketing Director.
Generate a comprehensive, high-converting 6-channel marketing campaign package for the following property.

### PROPERTY DATA:
- Property Title: {prop_title}
- Location: {prop_location}
- Price: {prop_price}
- Property Type: {prop_type}
- Size: {prop_size}
- Specs & Amenities: {prop_specs}
- Conversion Strategy Angle: {campaign_angle}
- Output Language: {target_language} (Note: If a regional language with native script like Tamil, Hindi, Telugu, Kannada, or Malayalam is selected, write the copy fluently in that native script with natural regional real-estate vocabulary).

### AGENT BRANDING:
- Agent/Agency: {display_agent}
- Contact Phone: {agent_phone or 'Contact on Request'}
- Email: {agent_email or 'Contact on Request'}
- RERA ID: {agent_rera or 'Available on Request'}
- Direct WhatsApp Inquiry Link: {wa_link}

### MULTIMODAL INSTRUCTION:
If property images or video clips are provided, examine them carefully to identify key interior features, architectural highlights, natural lighting, and premium fixtures. Seamlessly highlight these authentic visual details in the copy.

### FORMATTING REQUIREMENTS:
Generate high-performing, ready-to-copy marketing copy strictly formatted as a valid JSON object with the following keys:
{{
  "whatsapp_blast": "Punchy, emoji-rich broadcast copy tailored for WhatsApp buyer groups. Must include bold headlines, bulleted USPs, pricing, and the clickable WhatsApp CTA link.",
  "email_campaign": "Complete HTML/Markdown email newsletter with a high open-rate Subject Line, Preview Text, Engaging Body Copy, Bulleted Feature Sheet, and Clear Booking Call to Action.",
  "instagram_caption": "Engaging feed & carousel caption with an attention-grabbing first-line hook, lifestyle aesthetic narrative, bullet points, CTA to DM/WhatsApp, and 15 targeted hashtags.",
  "facebook_ad": "Conversational, community-focused Facebook ad copy with Primary Text, Catchy Headline, Link Description, and CTA.",
  "mls_portal_description": "Professional, descriptive, and compliance-checked listing overview suitable for MLS, 99acres, Housing.com, Magicbricks, or Zillow. Formal yet compelling.",
  "reel_script": "30-45 second short-form video reel script with timestamps, visual cues (b-roll instructions), and voiceover narration designed for Instagram Reels/YouTube Shorts."
}}
Return ONLY raw, valid JSON. Do not include markdown code block backticks outside the JSON.
"""

            try:
                contents_payload = [prompt_text]
                
                # Multi-Image Attachment
                if uploaded_photos:
                    for photo in uploaded_photos:
                        contents_payload.append(Image.open(photo))

                # Video Attachment via Gemini Files API
                if uploaded_video:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                        tmp_file.write(uploaded_video.read())
                        tmp_video_path = tmp_file.name
                    
                    video_upload_ref = client.files.upload(file=tmp_video_path)
                    contents_payload.append(video_upload_ref)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents_payload,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                result_data = json.loads(response.text)
                st.session_state["campaign_result"] = result_data
                st.session_state["wa_link"] = wa_link
                st.success("🎉 Campaign generated successfully across all 6 channels!")

            except Exception as e:
                st.error(f"Error generating campaign: {str(e)}")

# -------------------------------------------------------------
# Display Campaign Outputs
# -------------------------------------------------------------
if "campaign_result" in st.session_state:
    res = st.session_state["campaign_result"]
    wa_link = st.session_state.get("wa_link", "#")

    st.markdown("### 📦 Your Multi-Channel Campaign Kit")

    tab_wa, tab_email, tab_ig, tab_fb, tab_mls, tab_reel = st.tabs([
        "⚡ WhatsApp Broadcast",
        "✉️ Email Newsletter",
        "📸 Instagram & TikTok",
        "🌐 Facebook Post / Ad",
        "📋 MLS & Portal Listing",
        "🎬 30s Reel Script"
    ])

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
        st.subheader("MLS & Property Portal Description")
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