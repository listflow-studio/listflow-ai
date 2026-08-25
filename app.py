import os
import re
import io
import time
import urllib.request
import tempfile
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from google import genai
from google.genai import types
from gtts import gTTS

# MoviePy Import (Compatible with v1.x and v2.x)
MOVIEPY_AVAILABLE = False
try:
    from moviepy import ImageClip, concatenate_videoclips, AudioFileClip, ImageSequenceClip
    MOVIEPY_AVAILABLE = True
except Exception:
    try:
        from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, ImageSequenceClip
        MOVIEPY_AVAILABLE = True
    except Exception:
        MOVIEPY_AVAILABLE = False

# ---------------------------------------------------------
# Page Configuration & Modern SaaS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="ListFlow AI — Real Estate Marketing Studio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 14px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
    }
    
    .saas-badge {
        display: inline-block;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        color: white;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        margin-bottom: 0.5rem;
    }

    .saas-title {
        color: #FFFFFF !important;
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .saas-subtitle {
        color: #94A3B8 !important;
        font-size: 0.92rem !important;
        margin-top: 0.3rem;
        margin-bottom: 0;
    }

    .metric-pill {
        background: rgba(37, 99, 235, 0.12);
        border: 1px solid rgba(37, 99, 235, 0.25);
        color: #60A5FA;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.76rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #0F172A;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #1E293B;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: nowrap;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0px 14px;
        border-radius: 8px;
        color: #94A3B8;
        background-color: transparent;
        transition: all 0.2s ease-in-out;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Local Font Auto-Downloader (Guarantees Sharp TrueType Fonts)
# ---------------------------------------------------------
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
os.makedirs(FONT_DIR, exist_ok=True)
LOCAL_BOLD_FONT = os.path.join(FONT_DIR, "Inter-Bold.ttf")

if not os.path.exists(LOCAL_BOLD_FONT):
    try:
        font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf"
        urllib.request.urlretrieve(font_url, LOCAL_BOLD_FONT)
    except Exception:
        pass

def get_bundled_font(size=28):
    """Loads bundled TrueType font; falls back to system fonts if needed."""
    if os.path.exists(LOCAL_BOLD_FONT):
        try:
            return ImageFont.truetype(LOCAL_BOLD_FONT, size)
        except Exception:
            pass
    for path in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\segoeuib.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------------------------------------------------------
# Dynamic Reset Routine
# ---------------------------------------------------------
def reset_entire_studio():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ---------------------------------------------------------
# API Client Initialization
# ---------------------------------------------------------
def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        secrets_path = os.path.join(os.path.dirname(__file__), "secrets.txt")
        if os.path.exists(secrets_path):
            with open(secrets_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break
                    elif line and not line.startswith("#"):
                        api_key = line
                        break
    if not api_key:
        st.sidebar.error("❌ Gemini API Key missing in environment or secrets.txt.")
        st.stop()
    return genai.Client(api_key=api_key)

# ---------------------------------------------------------
# Text Cleanser & Language Mapping
# ---------------------------------------------------------
def clean_display_text(text):
    if not text:
        return ""
    clean = re.sub(r'[\U00010000-\U0010ffff]', '', str(text))
    clean = re.sub(r'[📞🌐🔥✨📈🏡🚨🌟🌿💰🎬⚡✉️📸👥📄⬇️📦🔄*`_~]', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def get_gtts_lang_code(selected_language_name):
    lang_str = str(selected_language_name).lower()
    if "english" in lang_str: return "en"
    elif "tamil" in lang_str or "தமிழ்" in lang_str or "tanglish" in lang_str: return "ta"
    elif "hindi" in lang_str or "हिंदी" in lang_str or "hinglish" in lang_str: return "hi"
    elif "telugu" in lang_str or "తెలుగు" in lang_str: return "te"
    elif "kannada" in lang_str or "ಕನ್ನಡ" in lang_str: return "kn"
    elif "malayalam" in lang_str or "മലയാളம்" in lang_str: return "ml"
    return "en"

def extract_reel_scenes(script_text):
    spoken_lines = []
    screen_cues = []
    
    for line in script_text.split('\n'):
        clean = re.sub(r'[*_#`~]', '', line).strip()
        m_vo = re.search(r'(?:voiceover|voice\s*over|vo|audio|narration|குரல்|ஆடியோ|आवाज़)\s*:\s*(.*)', clean, re.IGNORECASE)
        if m_vo and m_vo.group(1).strip():
            spoken_lines.append(m_vo.group(1).strip())
                
        m_screen = re.search(r'(?:on-screen|on\s*screen|onscreen|text\s*hook|hook)\s*:\s*(.*)', clean, re.IGNORECASE)
        if m_screen and m_screen.group(1).strip():
            screen_cues.append(m_screen.group(1).strip())

    clean_vo = " ".join(spoken_lines) if spoken_lines else script_text
    clean_vo = re.sub(r'\*+|\[.*?\]|\(.*?\)', '', clean_vo)
    clean_vo = re.sub(r'\b(visual|camera|on-screen|scene\s*\d+):', '', clean_vo, flags=re.IGNORECASE)
    clean_vo = " ".join(clean_vo.split())
    words = clean_vo.split()
    final_speech = " ".join(words[:50]) if words else "Check details below to book your private tour."
    
    return final_speech, screen_cues

# ---------------------------------------------------------
# Dynamic Motion + TrueType Graphic Overlay Engine
# ---------------------------------------------------------
def create_motion_clip_with_overlays(pil_img, duration, fps, zoom_in, top_badge, caption_text, contact_text):
    """Generates Ken Burns zoom motion with TrueType text overlay composite."""
    target_w, target_h = 720, 1280
    num_frames = max(int(duration * fps), 1)

    # Base Crop 9:16
    img_ratio = pil_img.width / pil_img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        nh = target_h
        nw = int(target_h * img_ratio)
    else:
        nw = target_w
        nh = int(target_w / img_ratio)

    base_img = pil_img.resize((nw, nh), Image.Resampling.BILINEAR)
    left = (nw - target_w) // 2
    top = (nh - target_h) // 2
    base_916 = base_img.crop((left, top, left + target_w, top + target_h))

    # Pre-render Graphic Overlay Mask
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_badge = get_bundled_font(size=22)
    font_caption = get_bundled_font(size=30)
    font_contact = get_bundled_font(size=20)

    clean_badge = clean_display_text(top_badge)
    clean_caption = clean_display_text(caption_text)
    clean_contact = clean_display_text(contact_text)

    # 1. Top Glass Badge
    if clean_badge:
        pill_w = min(target_w - 60, 640)
        px1 = (target_w - pill_w) // 2
        px2 = px1 + pill_w
        draw.rounded_rectangle([px1, 40, px2, 105], radius=16, fill=(15, 23, 42, 235), outline=(59, 130, 246, 255), width=2)
        draw.text((target_w // 2, 72), clean_badge[:45], font=font_badge, fill=(255, 255, 255, 255), anchor="mm")

    # 2. Modern Subtitle Card
    if clean_caption:
        words = clean_caption.split()
        lines = []
        cur = []
        for word in words:
            cur.append(word)
            if len(" ".join(cur)) > 24:
                lines.append(" ".join(cur[:-1]))
                cur = [word]
        if cur:
            lines.append(" ".join(cur))
        
        display_caption = "\n".join(lines[:2])
        card_h = 100 if len(lines) <= 1 else 130
        cy1 = target_h - 320
        cy2 = cy1 + card_h
        
        # Glow backing + Card
        draw.rounded_rectangle([40, cy1, target_w - 40, cy2], radius=18, fill=(10, 15, 29, 230), outline=(250, 204, 21, 230), width=2)
        draw.text((target_w // 2, (cy1 + cy2) // 2), display_caption, font=font_caption, fill=(254, 240, 138, 255), anchor="mm", align="center")

    # 3. Bottom Contact Banner
    if clean_contact:
        draw.rectangle([0, target_h - 100, target_w, target_h], fill=(15, 23, 42, 245))
        draw.line([(0, target_h - 100), (target_w, target_h - 100)], fill=(37, 99, 235, 255), width=3)
        draw.text((target_w // 2, target_h - 50), clean_contact[:65], font=font_contact, fill=(255, 255, 255, 255), anchor="mm")

    # Render Frames with Subtle Ken Burns Motion (1.0x to 1.12x zoom)
    frames = []
    for i in range(num_frames):
        progress = i / max(num_frames - 1, 1)
        scale = 1.0 + (0.12 * progress) if zoom_in else 1.12 - (0.12 * progress)
        
        zw = int(target_w * scale)
        zh = int(target_h * scale)
        scaled_frame = base_916.resize((zw, zh), Image.Resampling.BILINEAR)
        
        # Center crop back to 720x1280
        zleft = (zw - target_w) // 2
        ztop = (zh - target_h) // 2
        cropped_frame = scaled_frame.crop((zleft, ztop, zleft + target_w, ztop + target_h)).convert("RGBA")
        
        # Alpha composite overlay
        final_frame = Image.alpha_composite(cropped_frame, overlay).convert("RGB")
        frames.append(np.array(final_frame))

    return frames

# ---------------------------------------------------------
# Fast 9:16 MP4 Motion Reel Generator
# ---------------------------------------------------------
def generate_fast_mp4_reel(images, script_text, selected_language, top_badge, contact_info):
    if not MOVIEPY_AVAILABLE or not images:
        return None

    clean_voiceover, screen_cues = extract_reel_scenes(script_text)
    tts_lang = get_gtts_lang_code(selected_language)

    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "voiceover.mp3")
    video_path = os.path.join(temp_dir, "reel_output.mp4")

    audio_clip = None
    final_video = None

    try:
        # 1. Voiceover Audio Generation
        try:
            tts = gTTS(text=clean_voiceover, lang=tts_lang, slow=False)
            tts.save(audio_path)
        except Exception:
            tts = gTTS(text=clean_voiceover, lang="en", slow=False)
            tts.save(audio_path)

        audio_clip = AudioFileClip(audio_path)
        total_duration = max(audio_clip.duration, 5.0)
        duration_per_img = total_duration / len(images)
        fps = 20

        # 2. Build Motion Frames
        all_frames = []
        for idx, img_file in enumerate(images):
            img_file.seek(0)
            pil_img = Image.open(img_file).convert("RGB")
            
            caption = screen_cues[idx] if idx < len(screen_cues) else ""
            if not caption and idx == 0 and screen_cues:
                caption = screen_cues[0]

            zoom_in = (idx % 2 == 0)
            clip_frames = create_motion_clip_with_overlays(
                pil_img, duration_per_img, fps, zoom_in, top_badge, caption, contact_info
            )
            all_frames.extend(clip_frames)

        # 3. Stitch Video with Motion
        try:
            final_video = ImageSequenceClip(all_frames, fps=fps)
        except Exception:
            import moviepy.video.io.ImageSequenceClip as mpy_seq
            final_video = mpy_seq.ImageSequenceClip(all_frames, fps=fps)

        if hasattr(final_video, 'with_audio'):
            final_video = final_video.with_audio(audio_clip)
        else:
            final_video = final_video.set_audio(audio_clip)

        final_video.write_videofile(
            video_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=4,
            logger=None
        )

        with open(video_path, "rb") as vf:
            video_bytes = vf.read()

        return video_bytes

    except Exception as e:
        st.warning(f"Video engine note: {e}")
        return None
    finally:
        if audio_clip:
            try: audio_clip.close()
            except Exception: pass
        if final_video:
            try: final_video.close()
            except Exception: pass

# ---------------------------------------------------------
# Sidebar: Language & Agent Branding
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 Regional Language")
    selected_lang = st.selectbox(
        "Language / Dialect:",
        [
            "English (Global / Standard)",
            "Tamil (தமிழ்)",
            "Hindi (हिंदी)",
            "Telugu (తెలుగు)",
            "Kannada (ಕನ್ನಡ)",
            "Malayalam (മലയാളം)",
            "Tanglish (Tamil + English Hybrid)",
            "Hinglish (Hindi + English Hybrid)"
        ],
        key="f_lang"
    )

    st.markdown("---")
    st.markdown("### 👤 Agent & Broker Details")
    agent_name = st.text_input("Agent Name", placeholder="e.g., Rajesh Kumar", key="f_agent_name")
    agency_name = st.text_input("Brokerage / Agency", placeholder="e.g., Prime Realty", key="f_agency_name")
    agent_phone = st.text_input("WhatsApp / Phone", placeholder="e.g., +91 98765 43210", key="f_agent_phone")
    agent_web = st.text_input("Website / Listing Link", placeholder="e.g., primerealty.in", key="f_agent_web")
    agent_rera = st.text_input("RERA / License ID", placeholder="e.g., TN/01/Building/2026/XXXX", key="f_agent_rera")

    st.markdown("---")
    st.button("🔄 Reset Studio", on_click=reset_entire_studio, use_container_width=True)

# ---------------------------------------------------------
# Main Header
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div class="saas-badge">High-Conversion Marketing Studio</div>
    <div class="saas-title">ListFlow AI Studio</div>
    <div class="saas-subtitle">Transform property specs, photos, and videos into multi-channel campaigns sorted by revenue & lead velocity.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Intake Form
# ---------------------------------------------------------
col_left, col_right = st.columns([1.1, 0.9], gap="medium")

with col_left:
    st.markdown("#### 1. Property Details & Ad Angle")
    
    ad_angle = st.selectbox(
        "🔥 Campaign Angle & Headline Style:",
        [
            "🔥 HOT Deal / Urgent Exclusive Sale",
            "✨ Ultra-Luxury / Premium Collection",
            "📈 High-ROI Investment Pick (High Yield / Capital Growth)",
            "🏡 Ready-to-Move Family Haven (Comfort & Schools)",
            "🚨 Price Drop / Exclusive Distress Opportunity",
            "🌟 Newly Launched / Early-Bird Pre-Booking",
            "🌿 Serene Eco-Living / Spacious Retreat"
        ],
        key="f_angle"
    )

    prop_type = st.selectbox(
        "Property Type",
        ["3 BHK Luxury Apartment", "4 BHK Villa", "Independent House", "Commercial Office", "Residential Plot", "Penthouse"],
        key="f_prop_type"
    )
    loc = st.text_input("Location / Locality", placeholder="e.g., Anna Nagar, Chennai / Whitefield, Bangalore", key="f_loc")
    price = st.text_input("Price / Pricing Term", placeholder="e.g., ₹1.85 Cr or ₹45,000 / month", key="f_price")
    key_features = st.text_area(
        "Key Selling Points & Amenities",
        placeholder="e.g., 2200 sq.ft, East-facing, Italian marble, EV charger, 2 covered car parking, Metro 500m away...",
        height=120,
        key="f_features"
    )

with col_right:
    st.markdown("#### 2. Media Assets (Multimodal)")
    uploaded_images = st.file_uploader(
        "Property Photos (Upload 2-6 for best Video Reel)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="f_images"
    )
    if uploaded_images:
        st.caption(f"📸 {len(uploaded_images)} photos loaded")
        preview_cols = st.columns(min(len(uploaded_images), 4))
        for idx, img in enumerate(uploaded_images[:4]):
            with preview_cols[idx]:
                st.image(img, use_container_width=True)

    uploaded_video = st.file_uploader(
        "Walkthrough Video (Optional)",
        type=["mp4", "mov", "webm"],
        key="f_video",
        help="Gemini analyzes layout flow and finishes directly from video."
    )

generate_btn = st.button("🚀 Generate Marketing Campaign", type="primary", use_container_width=True)

# ---------------------------------------------------------
# Generation Execution
# ---------------------------------------------------------
if generate_btn:
    if not loc or not price:
        st.error("Please enter at least the Location and Price to generate the campaign.")
    else:
        with st.spinner(f"Creating campaign in {selected_lang}..."):
            client = get_gemini_client()
            
            clean_phone = re.sub(r'[^0-9]', '', agent_phone)
            wa_link = f"https://wa.me/{clean_phone}" if clean_phone else "[Direct WhatsApp Link]"

            prompt_content = f"""
            You are an elite real estate growth marketer. Generate a high-conversion 6-channel marketing campaign based on the provided details and media.

            ### CRITICAL LANGUAGE INSTRUCTION:
            The user explicitly selected: {selected_lang}
            - If English is selected, ALL content and scripts MUST be in 100% natural, fluent English.
            - If a regional language is selected, generate all copy natively in that script.

            ### CAMPAIGN ANGLE:
            {ad_angle}

            ### PROPERTY INFORMATION:
            - Property Type: {prop_type}
            - Location: {loc}
            - Price: {price}
            - Features & Amenities: {key_features}

            ### AGENT BRANDING:
            - Agent Name: {agent_name or '[Agent Name]'}
            - Agency / Brokerage: {agency_name or '[Agency]'}
            - Contact Number: {agent_phone or '[Contact Number]'}
            - WhatsApp Link: {wa_link}
            - Website: {agent_web or '[Website Link]'}
            - RERA ID: {agent_rera or '[RERA Registered]'}

            ### OUTPUT FORMAT RULES:
            Provide EXACTLY 6 sections with these exact header tags. Do NOT use markdown bolding (**) inside the spoken voiceover lines.

            ===WHATSAPP===
            (High-velocity pitch under 60 words. Emphasize price, locality, instant visit booking, and inject {wa_link} as the CTA).

            ===EMAIL===
            (Subject Line reflecting the headline angle, preview text, investor/buyer value pitch, bulleted highlights, agent signature, and booking CTA).

            ===REEL_SCRIPT===
            Scene 1:
            Visual: [Brief camera action]
            Voiceover: [Exact spoken narration text in {selected_lang}. No asterisks.]
            On-Screen: [Punchy 3-5 word caption hook]

            Scene 2:
            Visual: [Brief camera action]
            Voiceover: [Exact spoken narration text in {selected_lang}. No asterisks.]
            On-Screen: [Punchy 3-5 word caption hook]

            Scene 3:
            Visual: [Brief camera action]
            Voiceover: [Exact spoken narration text in {selected_lang}. No asterisks.]
            On-Screen: [Punchy 3-5 word caption hook]

            ===INSTAGRAM===
            (High-impact hook line, aesthetic lifestyle copy, bulleted highlights, clear CTA, and 15 targeted real estate hashtags).

            ===FACEBOOK===
            (Community-focused storytelling, neighborhood amenities, open house invitation, clear CTA, and agent contact signature).

            ===MLS===
            (Formal listing title, structured specifications, aesthetic description, and search keywords).
            """

            contents = [prompt_content]

            if uploaded_images:
                for img_file in uploaded_images:
                    img_file.seek(0)
                    contents.append(Image.open(img_file))

            if uploaded_video:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tf:
                    tf.write(uploaded_video.read())
                    temp_video_path = tf.name
                
                video_file_ref = client.files.upload(file=temp_video_path)
                while video_file_ref.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file_ref = client.files.get(name=video_file_ref.name)
                contents.append(video_file_ref)

            models = ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-flash-latest"]
            response_text = ""
            for model_name in models:
                try:
                    res = client.models.generate_content(model=model_name, contents=contents)
                    response_text = res.text
                    break
                except Exception:
                    continue

            if not response_text:
                st.error("Failed to generate campaign. Please verify your Gemini API key.")
                st.stop()

            def parse_sec(tag, text):
                pattern = rf"==={tag}===\s*(.*?)(?====|\Z)"
                m = re.search(pattern, text, re.DOTALL)
                return m.group(1).strip() if m else ""

            st.session_state["whatsapp"] = parse_sec("WHATSAPP", response_text)
            st.session_state["email"] = parse_sec("EMAIL", response_text)
            st.session_state["reel_script"] = parse_sec("REEL_SCRIPT", response_text)
            st.session_state["instagram"] = parse_sec("INSTAGRAM", response_text)
            st.session_state["facebook"] = parse_sec("FACEBOOK", response_text)
            st.session_state["mls"] = parse_sec("MLS", response_text)
            st.session_state["raw_response"] = response_text
            st.session_state["uploaded_images_ref"] = uploaded_images
            st.session_state["selected_lang"] = selected_lang
            
            clean_angle_title = clean_display_text(ad_angle.split('/')[0])
            st.session_state["cached_badge"] = f"{clean_angle_title} | {loc} - {price}"
            st.session_state["cached_contact"] = f"Call/WA: {agent_phone or 'Contact'} | Web: {agent_web or 'Book Tour'}"
            if "rendered_reel_bytes" in st.session_state:
                del st.session_state["rendered_reel_bytes"]

# ---------------------------------------------------------
# Output Hub (Sorted by Revenue & Reach Impact)
# ---------------------------------------------------------
if "raw_response" in st.session_state:
    st.markdown("---")
    st.markdown("### 📊 Generated Multi-Channel Campaign")
    st.caption("Channels are ordered by conversion speed & pipeline revenue impact.")

    tab_wa, tab_email, tab_reel, tab_ig, tab_fb, tab_mls = st.tabs([
        "⚡ WhatsApp (Lead Gen)",
        "✉️ Email (High Ticket)",
        "🎥 Video Reel & Script",
        "📸 Instagram (Reach)",
        "👥 Facebook (Local)",
        "📄 MLS / Portal Listing"
    ])

    with tab_wa:
        st.markdown('<span class="metric-pill">Conversion Speed: 🔥 Immediate (< 5 min)</span>', unsafe_allow_html=True)
        st.text_area("WhatsApp Copy", st.session_state.get("whatsapp", ""), height=220)
        st.download_button("📥 Download WhatsApp Copy", st.session_state.get("whatsapp", ""), file_name="whatsapp_pitch.txt", use_container_width=True)

    with tab_email:
        st.markdown('<span class="metric-pill">Revenue Impact: 💰 Highest Investor ROI</span>', unsafe_allow_html=True)
        st.text_area("Email Campaign", st.session_state.get("email", ""), height=340)
        st.download_button("📥 Download Email Campaign", st.session_state.get("email", ""), file_name="email_campaign.txt", use_container_width=True)

    with tab_reel:
        st.markdown('<span class="metric-pill">Reach: 🚀 Maximum Viral Discovery (9:16)</span>', unsafe_allow_html=True)
        
        st.markdown("#### 🎬 Ready-to-Post Video Reel")
        img_refs = st.session_state.get("uploaded_images_ref")
        current_lang = st.session_state.get("selected_lang", "English (Global / Standard)")
        top_badge = st.session_state.get("cached_badge", "Featured Property")
        contact_info = st.session_state.get("cached_contact", "Call / WhatsApp for Private Tour")

        if img_refs and len(img_refs) >= 1:
            if st.button("🎬 Create Video Reel", type="primary"):
                with st.spinner(f"Rendering Ken Burns motion reel & voiceover in {current_lang}..."):
                    video_data = generate_fast_mp4_reel(
                        img_refs, 
                        st.session_state.get("reel_script", ""), 
                        current_lang,
                        top_badge,
                        contact_info
                    )
                    if video_data:
                        st.session_state["rendered_reel_bytes"] = video_data
                        st.success("Cinematic motion reel created!")

            if "rendered_reel_bytes" in st.session_state:
                st.video(st.session_state["rendered_reel_bytes"])
                st.download_button(
                    label="⬇️ Download Video Reel",
                    data=st.session_state["rendered_reel_bytes"],
                    file_name="property_reel_9x16.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
        else:
            st.info("💡 Upload 2 or more property photos above to enable video reel creation.")

        st.markdown("---")
        st.text_area("Teleprompter / Voiceover Script", st.session_state.get("reel_script", ""), height=220)
        st.download_button("📥 Download Script", st.session_state.get("reel_script", ""), file_name="reel_script.txt", use_container_width=True)

    with tab_ig:
        st.markdown('<span class="metric-pill">Engagement: 📱 Visual Discovery & Lifestyle</span>', unsafe_allow_html=True)
        st.text_area("Instagram Caption", st.session_state.get("instagram", ""), height=320)
        st.download_button("📥 Download Instagram Caption", st.session_state.get("instagram", ""), file_name="instagram_caption.txt", use_container_width=True)

    with tab_fb:
        st.markdown('<span class="metric-pill">Audience: 🏡 Local Families & Community Buyers</span>', unsafe_allow_html=True)
        st.text_area("Facebook Post", st.session_state.get("facebook", ""), height=320)
        st.download_button("📥 Download Facebook Post", st.session_state.get("facebook", ""), file_name="facebook_post.txt", use_container_width=True)

    with tab_mls:
        st.markdown('<span class="metric-pill">Search: 🔍 Real Estate Portals & Catalog</span>', unsafe_allow_html=True)
        st.text_area("MLS Description", st.session_state.get("mls", ""), height=320)
        st.download_button("📥 Download Portal Listing", st.session_state.get("mls", ""), file_name="mls_listing.txt", use_container_width=True)

    st.markdown("---")
    st.download_button(
        label="📦 Download Complete Campaign Bundle (.txt)",
        data=st.session_state.get("raw_response", ""),
        file_name=f"ListFlow_Campaign_{loc.replace(' ', '_')}.txt",
        use_container_width=True
    )