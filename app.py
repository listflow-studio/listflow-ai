import os
import json
import urllib.parse
from PIL import Image
import streamlit as st
from google import genai
from google.genai import types

# -------------------------------------------------------------
# Streamlit Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="ListFlow AI | Real Estate Multi-Channel Studio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
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
    .badge-card {
        padding: 0.6rem 1rem;
        border-radius: 8px;
        background: #F1F5F9;
        border-left: 4px solid #2563EB;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Gemini Client Initialization
# -------------------------------------------------------------
def get_gemini_client():
    # Attempt to read from Streamlit secrets, then environment variable
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    elif os.environ.get("GEMINI_API_KEY"):
        api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ Gemini API Key not found! Please configure `GEMINI_API_KEY` in Streamlit Secrets or Environment Variables.")
        st.stop()
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# -------------------------------------------------------------
# Sidebar: Agent Profile, Support & Feedback
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&auto=format&fit=crop&q=80", use_container_width=True)
    st.title("🏢 ListFlow AI")
    st.caption("AI-Powered Multi-Channel Real Estate Studio")
    
    st.markdown("---")
    st.subheader("👤 Agent / Broker Profile")
    agent_name = st.text_input("Agent / Agency Name", value="Neyora Realty Services")
    agent_phone = st.text_input("WhatsApp / Phone Number", value="9884395952")
    agent_email = st.text_input("Contact Email", value="neyora.admin@gmail.com")
    agent_rera = st.text_input("RERA / License ID (Optional)", value="TN/AGENT/2026/00123")
    
    st.markdown("---")
    st.subheader("💬 Need Help or Have Feedback?")
    
    support_email = "neyora.admin@gmail.com"
    email_subject = "ListFlow%20AI%20Support%20%26%20Feedback"
    whatsapp_number = "919884395952"
    whatsapp_msg = "Hi%20Neyora%20Team%2C%20I%20have%20a%20question%20about%20ListFlow%20AI."
    
    st.markdown(
        f"""
        * 📧 **Email:** [{support_email}](mailto:{support_email}?subject={email_subject})
        * 💬 **WhatsApp:** [Chat with Us](https://wa.me/{whatsapp_number}?text={whatsapp_msg})
        """
    )
    
    with st.expander("📝 Quick Feedback"):
        feedback_text = st.text_area("Share your thoughts or feature requests:", height=80, key="quick_feedback")
        if st.button("Submit Feedback", use_container_width=True):
            if feedback_text.strip():
                st.success("Thank you! Your feedback has been noted.")
            else:
                st.warning("Please enter a short note before submitting.")

    st.caption("Powered by Neyora Studios • Version 1.0.0")

# -------------------------------------------------------------
# Main Application Interface
# -------------------------------------------------------------
st.markdown('<div class="main-title">ListFlow AI — Real Estate Launch Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Turn property specs and photos into high-converting 6-channel marketing campaigns in seconds.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 0.9], gap="medium")

with col1:
    st.subheader("📝 Property Specifications")
    
    prop_title = st.text_input("Property Headline / Name", placeholder="e.g., Ultra-Luxury 3 BHK Penthouse in Anna Nagar")
    
    c1, c2 = st.columns(2)
    with c1:
        prop_location = st.text_input("Location / Neighborhood", placeholder="e.g., Anna Nagar West, Chennai")
        prop_price = st.text_input("Price / Price Range", placeholder="e.g., ₹1.85 Cr (Negotiable)")
    with c2:
        prop_type = st.selectbox("Property Type", ["Residential Apartment", "Independent Villa", "Plot / Land", "Commercial Space", "Penthouse", "Studio Apartment"])
        prop_size = st.text_input("Built-up Area / Carpet Area", placeholder="e.g., 1,850 sq.ft (Carpet)")
        
    prop_specs = st.text_area("Key Features & Amenities", placeholder="e.g., 3 Bedrooms, 3 Bathrooms, 2 Balconies, East Facing, Modular Kitchen, 2 Covered Car Parks, Swimming Pool, Clubhouse, 24/7 Security.", height=110)

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
        ]
    )
    
    target_language = st.selectbox(
        "Campaign Language / Tone",
        ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"]
    )
    
    uploaded_photo = st.file_uploader("Upload Property Photo (Optional Multimodal Vision)", type=["jpg", "jpeg", "png"])
    if uploaded_photo:
        preview_img = Image.open(uploaded_photo)
        st.image(preview_img, caption="Uploaded Property Photo", use_container_width=True)

# -------------------------------------------------------------
# Campaign Generation Engine
# -------------------------------------------------------------
st.markdown("---")

generate_btn = st.button("🚀 Generate Multi-Channel Campaign", type="primary", use_container_width=True)

if generate_btn:
    if not prop_location or not prop_price or not prop_specs:
        st.warning("⚠️ Please provide at least the Location, Price, and Key Features before generating.")
    else:
        with st.spinner("✨ Gemini is crafting your 6-channel marketing campaign and analyzing visual highlights..."):
            
            clean_phone = "".join(filter(str.isdigit, agent_phone))
            if not clean_phone.startswith("91") and len(clean_phone) == 10:
                clean_phone = f"91{clean_phone}"
            
            wa_inquiry_msg = urllib.parse.quote(f"Hi {agent_name}, I am interested in the {prop_title or 'property'} at {prop_location} priced at {prop_price}. Please share full details.")
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
- Output Language: {target_language}

### AGENT BRANDING:
- Agent/Agency: {agent_name}
- Contact Phone: {agent_phone}
- Email: {agent_email}
- RERA ID: {agent_rera}
- Direct WhatsApp Inquiry Link: {wa_link}

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
                if uploaded_photo:
                    image_obj = Image.open(uploaded_photo)
                    contents_payload.append(image_obj)

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