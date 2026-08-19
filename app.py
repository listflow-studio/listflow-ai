import streamlit as st
import re
import os
import tempfile
from PIL import Image
from google import genai

# Page configuration
st.set_page_config(
    page_title="ListFlow AI - Real Estate Studio",
    page_icon="🏢",
    layout="wide"
)

# Custom CSS for compact tabs & responsive layout
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .sub-caption {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #E0E7FF;
        color: #4338CA;
        margin-bottom: 0.4rem;
    }
    
    /* Compact tab styling to ensure all 6 tabs stay visible */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    .stTabs [data-baseweb="tab"] p {
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Client Initializer
@st.cache_resource
def get_gemini_client():
    try:
        with open("secrets.txt", "r") as f:
            api_key = f.read().strip()
        return genai.Client(api_key=api_key)
    except FileNotFoundError:
        st.error("Missing `secrets.txt`. Please ensure your API key file exists in the directory.")
        return None

client = get_gemini_client()

# Sample starter specs
STARTER_SPECS = """- Type: 3 BHK Luxury Apartment
- Size: 1,850 sq.ft
- Location: Indiranagar, Bangalore
- Key Features: East-facing, Italian marble flooring, 2 large balconies, modular kitchen with Bosch appliances.
- Society Amenities: Rooftop infinity pool, clubhouse, 24/7 power backup, gym.
- Price: ₹2.45 Crore
- Target Buyer: Tech executives / young families looking for prime connectivity."""

# Session state initialization
if "specs_input" not in st.session_state:
    st.session_state["specs_input"] = STARTER_SPECS
if "reset_counter" not in st.session_state:
    st.session_state["reset_counter"] = 0

def clear_all():
    st.session_state["specs_input"] = ""
    st.session_state["reset_counter"] += 1
    if "parsed_output" in st.session_state:
        del st.session_state["parsed_output"]
    if "last_output" in st.session_state:
        del st.session_state["last_output"]

def generate_listing_assets(property_details: str, tone: str, images_list, video_file) -> str:
    """Sends text specs, photos, and video to Gemini Flash."""
    prompt = f"""
    You are an elite real estate copywriter and creative producer. Convert the provided property specs and media into 6 distinct marketing assets.
    
    Writing Tone: {tone}
    
    Structure your entire response clearly into these 6 exact Markdown sections:
    ## 1. MLS / Portal Listing
    (Professional, exhaustive, search-optimized, structured with bulleted specs and aesthetic notes)
    
    ## 2. Instagram Caption
    (Punchy hook, lifestyle appeal with emojis, clean line breaks, visual aesthetic notes, and 8-10 targeted real estate hashtags)

    ## 3. Facebook Post
    (Community & lifestyle focused, engaging headline, key highlights, open house/inquiry invite, and [Link in Bio / Comment below] call-to-action)
    
    ## 4. Direct Email Blast
    (High-open subject line, concise value proposition, clear Call-to-Action for scheduling a site visit)
    
    ## 5. WhatsApp / SMS Quick Pitch
    (Concise, under 60 words, direct, high-impact, easy to read on mobile)

    ## 6. Short-Form Video / Reel Script
    (Complete 30-45 second video script formatted in a table or structured breakdown with:
    - [Timecode / Scene]
    - [Visual & Camera Direction / Movement]
    - [Voiceover Narration / Spoken Hook]
    - [On-Screen Text Overlay])
    
    Property Specs:
    {property_details}
    """
    
    contents = [prompt]
    
    # Process images
    if images_list:
        for img in images_list:
            contents.append(img)
        prompt += f"\nNote: Incorporate visual observations from the {len(images_list)} attached property photo(s)."

    # Process video
    if video_file is not None:
        suffix = os.path.splitext(video_file.name)[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(video_file.getvalue())
            tmp_path = tmp.name

        try:
            uploaded_gemini_file = client.files.upload(file=tmp_path)
            contents.append(uploaded_gemini_file)
            prompt += "\nNote: Incorporate spatial flow and movement from the attached walkthrough video."
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-3.5-flash",
        "gemini-3.7-flash",
        "gemini-flash-latest"
    ]
    
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            last_error = e
            continue
            
    raise last_error

def parse_sections(raw_text: str):
    sections = {
        "mls": "No MLS listing generated.",
        "instagram": "No Instagram caption generated.",
        "facebook": "No Facebook post generated.",
        "email": "No Email blast generated.",
        "whatsapp": "No WhatsApp pitch generated.",
        "video": "No Video script generated."
    }
    
    mls_match = re.search(r"## 1\..*?\n(.*?)(?=## 2\.|\Z)", raw_text, re.DOTALL)
    insta_match = re.search(r"## 2\..*?\n(.*?)(?=## 3\.|\Z)", raw_text, re.DOTALL)
    fb_match = re.search(r"## 3\..*?\n(.*?)(?=## 4\.|\Z)", raw_text, re.DOTALL)
    email_match = re.search(r"## 4\..*?\n(.*?)(?=## 5\.|\Z)", raw_text, re.DOTALL)
    wa_match = re.search(r"## 5\..*?\n(.*?)(?=## 6\.|\Z)", raw_text, re.DOTALL)
    video_match = re.search(r"## 6\..*?\n(.*?)(?=\Z)", raw_text, re.DOTALL)
    
    if mls_match: sections["mls"] = mls_match.group(1).strip()
    if insta_match: sections["instagram"] = insta_match.group(1).strip()
    if fb_match: sections["facebook"] = fb_match.group(1).strip()
    if email_match: sections["email"] = email_match.group(1).strip()
    if wa_match: sections["whatsapp"] = wa_match.group(1).strip()
    if video_match: sections["video"] = video_match.group(1).strip()
        
    return sections

# --- UI Header ---
st.markdown('<div class="badge">ListFlow AI • Property Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">Real Estate Marketing Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-caption">Generate a complete 6-channel marketing campaign and video script for your property</div>', unsafe_allow_html=True)

# Layout: Adjusted ratio gives ample room for all 6 tabs on the right
col1, col2 = st.columns([0.85, 1.15], gap="large")

with col1:
    st.subheader("1. Property Details & Media")
    
    property_input = st.text_area(
        label="Enter Property Specifications:",
        value=st.session_state["specs_input"],
        height=170,
        placeholder="Enter property type, location, size, key features, pricing, and amenities..."
    )
    st.session_state["specs_input"] = property_input

    # Multi-Image Uploader
    uploaded_images = st.file_uploader(
        label="📸 Upload Property Photos (JPG/PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"photos_{st.session_state['reset_counter']}"
    )
    
    pil_images = []
    if uploaded_images:
        img_cols = st.columns(min(len(uploaded_images), 3))
        for idx, uploaded_file in enumerate(uploaded_images):
            img = Image.open(uploaded_file)
            pil_images.append(img)
            with img_cols[idx % 3]:
                st.image(img, caption=f"Photo #{idx+1}", use_container_width=True)

    # Video Walkthrough Uploader
    uploaded_video = st.file_uploader(
        label="🎥 Optional: Upload Walkthrough Video (MP4/MOV)",
        type=["mp4", "mov", "webm"],
        key=f"video_{st.session_state['reset_counter']}"
    )
    if uploaded_video:
        st.video(uploaded_video)

    tone_choice = st.selectbox(
        label="Campaign Tone & Target Audience:",
        options=[
            "Luxury & Sophisticated",
            "High-Energy & Urgent (Investor / Hot Deal)",
            "Warm, Family-Friendly & Welcoming",
            "Minimalist & Modern Architectural"
        ]
    )

    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        generate_button = st.button("✨ Generate 6-Channel Campaign", type="primary", use_container_width=True)
    with btn_col2:
        st.button("🗑️ Reset", on_click=clear_all, use_container_width=True)

with col2:
    st.subheader("2. Campaign Output")
    
    if generate_button:
        if not property_input.strip():
            st.warning("Please enter some property specifications first.")
        elif client is None:
            st.error("API client not initialized. Check your `secrets.txt` file.")
        else:
            with st.spinner("Analyzing property details & generating campaign assets..."):
                try:
                    raw_output = generate_listing_assets(property_input, tone_choice, pil_images, uploaded_video)
                    parsed = parse_sections(raw_output)
                    
                    st.session_state["last_output"] = raw_output
                    st.session_state["parsed_output"] = parsed
                except Exception as e:
                    st.error(f"Generation failed: {e}")
                    
    if "parsed_output" in st.session_state:
        parsed = st.session_state["parsed_output"]
        
        # Concise tab titles ensure all 6 tabs stay visible on one line
        tab_mls, tab_insta, tab_fb, tab_email, tab_wa, tab_vid = st.tabs([
            "📄 MLS", 
            "📸 Instagram", 
            "👥 Facebook", 
            "✉️ Email", 
            "💬 WhatsApp", 
            "🎥 Reel Script"
        ])
        
        with tab_mls:
            st.markdown(parsed.get("mls", ""))
            st.download_button("📥 Download MLS Text", data=parsed.get("mls", ""), file_name="property_mls.txt", mime="text/plain", use_container_width=True)
            
        with tab_insta:
            st.markdown(parsed.get("instagram", ""))
            st.download_button("📥 Download Instagram Caption", data=parsed.get("instagram", ""), file_name="property_instagram.txt", mime="text/plain", use_container_width=True)
            
        with tab_fb:
            st.markdown(parsed.get("facebook", ""))
            st.download_button("📥 Download Facebook Post", data=parsed.get("facebook", ""), file_name="property_facebook.txt", mime="text/plain", use_container_width=True)
            
        with tab_email:
            st.markdown(parsed.get("email", ""))
            st.download_button("📥 Download Email Copy", data=parsed.get("email", ""), file_name="property_email.txt", mime="text/plain", use_container_width=True)
            
        with tab_wa:
            st.markdown(parsed.get("whatsapp", ""))
            st.download_button("📥 Download WhatsApp Pitch", data=parsed.get("whatsapp", ""), file_name="property_whatsapp.txt", mime="text/plain", use_container_width=True)

        with tab_vid:
            st.markdown(parsed.get("video", ""))
            st.download_button("📥 Download Reel Script", data=parsed.get("video", ""), file_name="property_reel_script.txt", mime="text/plain", use_container_width=True)
            
        st.divider()
        st.download_button(
            label="📦 Download Complete 6-Channel Campaign Pack (.txt)",
            data=st.session_state.get("last_output", ""),
            file_name="property_complete_marketing_bundle.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("👈 Enter specs, upload photos/video, and click **Generate 6-Channel Campaign** to view outputs.")