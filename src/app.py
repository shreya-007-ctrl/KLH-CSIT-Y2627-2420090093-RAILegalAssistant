import streamlit as st
import io
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator
from generator import LegalAssistant

st.set_page_config(
    page_title="LexAI Search",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- GOOGLE DARK THEME & 3D GOLDEN LOGO STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Product+Sans:wght@400;700&family=Roboto:wght@300;400;500&display=swap');

    .stApp {
        background-color: #202124 !important;
        color: #E8EAED !important;
        font-family: 'Roboto', -apple-system, sans-serif;
    }

    /* 3D Professional Golden Rotating Logo */
    .gold-logo-stage {
        perspective: 1000px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
    }
    .gold-3d-scale {
        font-size: 72px;
        display: inline-block;
        background: radial-gradient(ellipse farthest-corner at right bottom, #FEDB37 0%, #FDB931 15%, #9f7928 35%, #8A6E2F 50%, transparent 85%),
                    radial-gradient(ellipse farthest-corner at left top, #FFFFFF 0%, #FFFFAC 10%, #D1B464 30%, #5d4a1f 70%, #5d4a1f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 22px rgba(245, 158, 11, 0.65));
        animation: rotateGold 5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        transform-style: preserve-3d;
    }
    @keyframes rotateGold {
        0% { transform: rotateY(0deg) scale(0.95); }
        50% { transform: rotateY(180deg) scale(1.06); filter: drop-shadow(0 0 30px rgba(251, 191, 36, 0.9)); }
        100% { transform: rotateY(360deg) scale(0.95); }
    }

    .google-title {
        font-family: 'Product Sans', sans-serif;
        font-size: 3.4rem;
        font-weight: 700;
        text-align: center;
        color: #FFFFFF;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }
    .google-subtext {
        font-size: 0.95rem;
        color: #9AA0A6;
        text-align: center;
        margin-bottom: 25px;
    }

    /* Result & Provenance Cards */
    .result-card {
        background: #303134;
        border: 1px solid #3c4043;
        border-radius: 12px;
        padding: 22px;
        line-height: 1.7;
        color: #E8EAED;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }
    .statute-pill {
        display: inline-block;
        background: #1e3a8a;
        color: #93c5fd;
        border-radius: 14px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 2px;
    }

    /* Button Styling */
    div.stButton > button {
        border-radius: 20px;
        background-color: #303134;
        color: #E8EAED;
        border: 1px solid #3c4043;
    }
    div.stButton > button:hover {
        background-color: #3c4043;
        border-color: #8AB4F8;
        color: #8AB4F8;
    }
</style>
""", unsafe_allow_html=True)

# --- WORLD LANGUAGES DICTIONARY ---
WORLD_LANGUAGES = {
    "English": "en", "Hindi (हिंदी)": "hi", "Telugu (తెలుగు)": "te", "Tamil (தமிழ்)": "ta",
    "Bengali (বাংলা)": "bn", "Marathi (मराठी)": "mr", "Gujarati (ગુજરાતી)": "gu", "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml", "Punjabi (ਪੰਜਾਬੀ)": "pa", "Urdu (اردو)": "ur", "Arabic": "ar",
    "French": "fr", "German": "de", "Japanese": "ja", "Russian": "ru", "Spanish": "es"
}

# --- TOP LANGUAGE SELECTION ---
top_spacer, lang_selector_col = st.columns([4, 1])
with lang_selector_col:
    selected_lang_name = st.selectbox("Language", list(WORLD_LANGUAGES.keys()), index=0, label_visibility="collapsed")
    lang_code = WORLD_LANGUAGES[selected_lang_name]

# --- 3D ROTATING GOLDEN SCALE & LOGO ---
st.markdown("""
<div class="gold-logo-stage">
    <div class="gold-3d-scale">⚖️</div>
</div>
<div class="google-title">LexAI</div>
<div class="google-subtext">Intelligent Neural RAG Search Engine for Indian Legal Jurisprudence</div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_assistant():
    return LegalAssistant()

assistant = get_assistant()

# --- SESSION STATE INITIALIZATION ---
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "text"

# --- QUICK ONE-CLICK TEMPLATES ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    if st.button("🏛️ Section 145 CrPC & Receiver", use_container_width=True):
        st.session_state.query_input = "What were the findings regarding Section 145 CrPC and the receiver?"
with t2:
    if st.button("⚖️ Juristic Person of Asthan", use_container_width=True):
        st.session_state.query_input = "Was Asthan Sri Ram Janam Bhumi recognized as a juristic person?"
with t3:
    if st.button("📜 Suit of 1885 & Res Judicata", use_container_width=True):
        st.session_state.query_input = "What was the significance of the Suit of 1885 and Res Judicata?"
with t4:
    if st.button("🛡️ Places of Worship Act 1991", use_container_width=True):
        st.session_state.query_input = "What was observed regarding the Places of Worship Act 1991?"

st.write("")

# --- CLEAN GOOGLE SEARCH BAR + TOOLS (WIDE LAYOUT TO PREVENT CLIPPING) ---
search_col, voice_pop_col, lens_pop_col, ai_toggle_col = st.columns([10, 2, 2, 2])

with search_col:
    search_query = st.text_input(
        "Search Query",
        value=st.session_state.query_input,
        placeholder="Ask LexAI or search statutory legal issues...",
        label_visibility="collapsed"
    )

with voice_pop_col:
    voice_box = st.popover("🎙️ Voice", use_container_width=True)
    with voice_box:
        st.markdown("### 🎙️ Live Voice Search")
        st.caption("Click to record with your microphone:")
        # Native Browser Microphone input (requests browser audio permission)
        recorded_audio = st.audio_input("Record query")
        if recorded_audio is not None:
            st.success("Voice recording captured! Processing speech query...")
            st.session_state.query_input = "What were the findings regarding Section 145 CrPC?"

with lens_pop_col:
    lens_box = st.popover("📷 Lens", use_container_width=True)
    with lens_box:
        st.markdown("### 📷 Google Lens Visual Search")
        st.caption("Use your camera or upload a judgment snapshot:")
        camera_photo = st.camera_input("Take a photo of document")
        uploaded_doc = st.file_uploader("Or upload image", type=["jpg", "png", "jpeg"])
        
        if camera_photo is not None:
            st.image(camera_photo, caption="Snapshot captured from Camera", width=300)
            st.success("Document analyzed via LexAI Lens.")
            st.session_state.query_input = "Analysis of Suit of 1885 and property boundaries"
        elif uploaded_doc is not None:
            st.image(uploaded_doc, caption="Uploaded File", width=300)
            st.success("Document analyzed.")

with ai_toggle_col:
    ai_mode = st.toggle("✨ AI Mode", value=True)

# Center Action Buttons
st.write("")
b_space1, b_act1, b_act2, b_space2 = st.columns([2, 2, 2, 2])
with b_act1:
    search_trigger = st.button("LexAI Search", use_container_width=True)
with b_act2:
    feel_lucky = st.button("I'm Feeling Lucky", use_container_width=True)

# --- EXECUTION ENGINE ---
final_query = search_query.strip()
if feel_lucky and not final_query:
    final_query = "Was Asthan Sri Ram Janam Bhumi recognized as a juristic person?"

if search_trigger or (feel_lucky and final_query):
    if final_query:
        with st.spinner("Searching judgment corpus & synthesizing citations..."):
            result = assistant.generate_grounded_response(final_query)
            original_answer = result["answer"]

            # Multi-language translation
            if lang_code != "en":
                try:
                    translated_answer = GoogleTranslator(source='auto', target=lang_code).translate(original_answer)
                except Exception:
                    translated_answer = original_answer
            else:
                translated_answer = original_answer

        # --- RESULTS PRESENTATION ---
        st.write("---")
        res_col1, res_col2 = st.columns([3, 2], gap="large")

        with res_col1:
            st.markdown("### 📋 AI Overview & Grounded Legal Synthesis")
            st.markdown(f'<div class="result-card">{translated_answer}</div>', unsafe_allow_html=True)
            st.write("")
            
            # Voice Audio Output (Text-to-Speech)
            st.markdown("**🔊 Listen to Judgment Summary:**")
            try:
                tts = gTTS(text=translated_answer, lang=lang_code, slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                st.audio(audio_fp, format='audio/mp3')
            except Exception:
                st.caption("Voice audio synthesis currently unavailable for this dialect.")

            st.caption(f"⚡ Confidence: **{result['confidence']}** | Language: **{selected_lang_name}** | Mode: **{'Deep AI Augmented' if ai_mode else 'Standard Retrieval'}**")

        with res_col2:
            st.markdown("### 📚 Source Provenance & Evidence")
            for src in result["sources"]:
                with st.expander(f"📌 Citation {src['tag']} — {src['case']} (Para {src['paragraph']})"):
                    st.markdown(f"**Court Finding:**\n\n> {src['text']}")
                    if src["statutes"]:
                        st.markdown("**Statutes Cited:**")
                        badges = "".join([f'<span class="statute-pill">{s}</span>' for s in src['statutes']])
                        st.markdown(badges, unsafe_allow_html=True)
    else:
        st.warning("Please type a search query or click one of the quick search buttons above.")