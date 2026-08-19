\# 🏢 ListFlow AI — Project Notes \& Architecture Log



\## 1. Project Overview

ListFlow AI is an AI-powered marketing studio for real estate professionals. It transforms raw property specifications, multiple high-resolution photos, and walkthrough videos into a complete 6-channel promotional campaign and short-form video script.



\---



\## 2. Core Architecture \& Tech Stack

\- \*\*Frontend / Framework:\*\* Streamlit (Python)

\- \*\*AI Core:\*\* Google GenAI SDK (`google-genai`)

\- \*\*Primary Model Routing:\*\* `gemini-2.5-flash` with dynamic failover (`gemini-3.5-flash`, `gemini-3.7-flash`, `gemini-flash-latest`)

\- \*\*Image Processing:\*\* Pillow (`PIL.Image`)

\- \*\*Video Processing:\*\* Temporary file caching + Google GenAI Files API

\- \*\*State Management:\*\* Streamlit `session\_state` for single-property intake, media persistence, and tab outputs



\---



\## 3. Marketing Output Channels

Every generation generates 6 distinct, structured deliverables:

1\. \*\*📄 MLS / Portal Listing:\*\* Structured specs, aesthetic highlights, SEO keywords.

2\. \*\*📸 Instagram Caption:\*\* Hook, lifestyle copy, emojis, clean line breaks, targeted hashtags.

3\. \*\*👥 Facebook Post:\*\* Community-oriented narrative, open house invitation, clear CTA.

4\. \*\*✉️ Email Blast:\*\* High-open subject line, investor/buyer value proposition, booking link.

5\. \*\*💬 WhatsApp / SMS Pitch:\*\* High-impact mobile copy under 60 words.

6\. \*\*🎥 Short-Form Reel Script:\*\* 30–45s breakdown with Timecode, Visual/Camera Direction, Voiceover Hook, and On-Screen Text.



\---



\## 4. Development Sprints Log



\### Sprint 1: Prototype \& Core Pipeline

\- Initialized Streamlit application structure.

\- Integrated `google-genai` client and local `secrets.txt` API key loader.

\- Implemented structured parsing engine for multi-section outputs.



\### Sprint 2: Multimodal Expansion

\- Added multi-image upload gallery with thumbnail preview grid.

\- Implemented video upload support (MP4/MOV/WEBM) with temporary file lifecycle management and Gemini File API upload.

\- Prompt updated to synthesize visual details from photos and spatial flow from videos.



\### Sprint 3: UI \& Workspace Optimization

\- Transitioned architecture to a focused, single-property studio.

\- Redesigned output panel to a 6-tab horizontal bar with compact CSS to ensure all tabs fit without clipping.

\- Added per-channel `.txt` download buttons and a single-click complete campaign bundle export.

\- Implemented a clean `clear\_all()` reset routine.



\### Sprint 4: Packaging \& Version Control

\- Structured `requirements.txt` with locked dependencies.

\- Added `.gitignore` to protect `secrets.txt`, virtual environments, and temporary files.

\- Drafted `README.md` project documentation.

\- Initialized local Git repository and created baseline commit.



\---



\## 5. Repository File Structure

```text

D:\\listflow-ai\\

├── .gitignore               # Security exclusions (secrets.txt, cache, temp media)

├── README.md                # Public project documentation \& setup instructions

├── requirements.txt         # Python dependencies

├── PROJECT\_NOTES.md         # Internal architecture log \& developer history

├── app.py                   # Main Streamlit engine \& UI application

└── secrets.txt              # Local Gemini API Key (Ignored by Git)

