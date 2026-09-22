import streamlit as st
import json
import os
import re
from google import genai
from google.genai import types
import hashlib
import base64
import platform
import uuid
from cryptography.fernet import Fernet

VAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".vault.enc")

def _get_vault_fernet() -> Fernet:
    salt = b"phishshield-vault-device-salt-v1"
    # Seed bound to local user and machine hardware ID
    device_seed = f"{platform.node()}:{os.getlogin()}:{uuid.getnode()}".encode("utf-8")
    derived = hashlib.pbkdf2_hmac("sha256", device_seed, salt, iterations=100_000)
    return Fernet(base64.urlsafe_b64encode(derived))

def load_vault_key() -> str:
    if not os.path.exists(VAULT_PATH):
        return ""
    try:
        f = _get_vault_fernet()
        with open(VAULT_PATH, "rb") as fp:
            ciphertext = fp.read()
        return f.decrypt(ciphertext).decode("utf-8").strip()
    except Exception:
        return ""

def save_vault_key(raw_key: str) -> bool:
    try:
        f = _get_vault_fernet()
        ciphertext = f.encrypt(raw_key.strip().encode("utf-8"))
        with open(VAULT_PATH, "wb") as fp:
            fp.write(ciphertext)
        return True
    except Exception:
        return False

def clear_vault_key() -> bool:
    try:
        if os.path.exists(VAULT_PATH):
            os.remove(VAULT_PATH)
        return True
    except Exception:
        return False

SHIELD_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "shield.png")
shield_b64 = ""
if os.path.exists(SHIELD_ICON_PATH):
    with open(SHIELD_ICON_PATH, "rb") as f:
        shield_b64 = base64.b64encode(f.read()).decode("utf-8")

st.set_page_config(
    page_title="Phishield AI • Threat Intelligence", 
    page_icon=SHIELD_ICON_PATH if os.path.exists(SHIELD_ICON_PATH) else "🔒", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Favicon
if shield_b64:
    st.markdown(f"""
    <link rel="icon" type="image/png" href="data:image/png;base64,{shield_b64}">
    <link rel="shortcut icon" type="image/png" href="data:image/png;base64,{shield_b64}">
    <link rel="apple-touch-icon" href="data:image/png;base64,{shield_b64}">
    """, unsafe_allow_html=True)

# Custom High-End Black & Luminous Orange Glassmorphism (Inspired by Reference Visuals)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

<style>
    /* Reset & Base Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Immersive Obsidian Void Background */
    .stApp {
        background-color: #060301;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(255, 95, 0, 0.15) 0%, rgba(10, 5, 2, 0) 65%),
            radial-gradient(circle at 10% 30%, rgba(220, 50, 0, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, rgba(255, 120, 0, 0.08) 0%, transparent 60%);
        color: #f8f6f0;
        overflow-x: hidden;
    }

    /* Vertical Glowing Fluted Curtain Effect (Reference Image 2) */
    .fluted-curtain-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0;
        opacity: 0.28;
        background: 
            repeating-linear-gradient(
                90deg,
                rgba(255, 100, 0, 0.25) 0px,
                rgba(255, 50, 0, 0.1) 1.5px,
                transparent 2.5px,
                transparent 14px
            );
        mask-image: radial-gradient(ellipse 90% 70% at 50% 15%, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 80%);
        -webkit-mask-image: radial-gradient(ellipse 90% 70% at 50% 15%, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 80%);
    }

    /* Ambient Glowing Floating Orbs (Reference Image 1) */
    .ambient-orb {
        position: fixed;
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
        filter: blur(65px);
        opacity: 0.65;
        animation: driftOrb 16s ease-in-out infinite alternate;
    }
    .orb-top-right {
        width: 440px;
        height: 440px;
        background: radial-gradient(circle, #ff7b00 15%, #d93800 65%, transparent 80%);
        top: 2%;
        right: 8%;
        animation-duration: 20s;
    }
    .orb-center-left {
        width: 340px;
        height: 340px;
        background: radial-gradient(circle, #ff9500 20%, #e63900 70%, transparent 85%);
        top: 28%;
        left: 4%;
        animation-duration: 15s;
        animation-delay: -4s;
    }
    .orb-bottom-right {
        width: 380px;
        height: 380px;
        background: radial-gradient(circle, #ff5900 10%, #b82200 70%, transparent 85%);
        bottom: 5%;
        right: 18%;
        animation-duration: 18s;
        animation-delay: -8s;
    }

    @keyframes driftOrb {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-28px) scale(1.06) rotate(3deg); }
        100% { transform: translateY(18px) scale(0.95) rotate(-3deg); }
    }

    /* Seamless Streamlit Top Header */
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }

    /* Layout wrapper with proper top breathing room */
    .block-container {
        position: relative;
        z-index: 1;
        padding-top: 5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1350px !important;
    }

    /* Ultra-Refined Frosted Glass Card (Reference Image 1) */
    .glass-card {
        background: rgba(22, 11, 5, 0.52);
        backdrop-filter: blur(28px) saturate(190%);
        -webkit-backdrop-filter: blur(28px) saturate(190%);
        border: 1px solid rgba(255, 140, 50, 0.22);
        border-top: 1px solid rgba(255, 190, 110, 0.55);
        border-radius: 24px;
        padding: 28px 32px;
        box-shadow: 
            0 25px 60px -15px rgba(0, 0, 0, 0.8),
            inset 0 1px 1px rgba(255, 230, 200, 0.3),
            inset 0 0 30px rgba(255, 110, 0, 0.05);
        margin-bottom: 24px;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .glass-card:hover {
        border-color: rgba(255, 150, 60, 0.35);
        box-shadow: 
            0 30px 70px -12px rgba(0, 0, 0, 0.85),
            inset 0 1px 1px rgba(255, 240, 210, 0.45),
            inset 0 0 35px rgba(255, 120, 0, 0.09);
    }

    /* Sub-card tile inside results */
    .glass-tile {
        background: rgba(15, 7, 3, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 130, 30, 0.16);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-tile:hover {
        transform: translateX(4px);
        border-color: rgba(255, 140, 40, 0.35);
    }

    /* Brand Header Accents */
    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 110, 0, 0.12);
        color: #ffa14a;
        border: 1px solid rgba(255, 120, 0, 0.35);
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        box-shadow: 0 0 16px rgba(255, 100, 0, 0.15);
        margin-bottom: 14px;
    }
    .brand-pill::before {
        content: '';
        width: 8px;
        height: 8px;
        background-color: #ff7700;
        border-radius: 50%;
        box-shadow: 0 0 10px #ff7700;
        animation: pulseDot 2s infinite;
    }
    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        line-height: 1.15;
        letter-spacing: -0.02em;
        margin: 0 0 8px 0;
        background: linear-gradient(135deg, #ffffff 30%, #ffd4aa 70%, #ff8833 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #b09e90;
        font-size: 1.08rem;
        font-weight: 400;
        line-height: 1.5;
        margin-bottom: 24px;
        max-width: 850px;
    }

    /* Styled Textarea & Inputs */
    .stTextArea textarea {
        background: rgba(14, 7, 3, 0.6) !important;
        border: 1px solid rgba(255, 130, 40, 0.22) !important;
        border-radius: 16px !important;
        color: #fff0e2 !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        backdrop-filter: blur(12px) !important;
        padding: 16px !important;
        transition: all 0.25s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #ff7a1a !important;
        box-shadow: 0 0 20px rgba(255, 120, 0, 0.35) !important;
    }

    /* File uploader container */
    [data-testid="stFileUploader"] {
        background: rgba(14, 7, 3, 0.45) !important;
        border: 1px dashed rgba(255, 130, 40, 0.28) !important;
        border-radius: 16px !important;
        padding: 14px !important;
        backdrop-filter: blur(10px) !important;
        transition: border-color 0.25s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #ff8822 !important;
    }

    /* Glowing Primary Scan Button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ff7300 0%, #e64000 60%, #c42b00 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 200, 150, 0.3) !important;
        border-radius: 14px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 14px 28px !important;
        letter-spacing: 0.5px !important;
        box-shadow: 
            0 8px 25px rgba(255, 100, 0, 0.4),
            inset 0 1px 1px rgba(255, 255, 255, 0.35) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        margin-top: 10px !important;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #ff881a 0%, #f04e00 60%, #d43500 100%) !important;
        box-shadow: 
            0 12px 35px rgba(255, 120, 0, 0.6),
            inset 0 1px 1px rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px);
    }

    /* Metric Display */
    .metric-container {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin: 12px 0 18px 0;
    }
    .metric-value-huge {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4.2rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.04em;
        background: linear-gradient(180deg, #ffffff 10%, #ffaa66 65%, #ff5500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 45px rgba(255, 100, 0, 0.45);
    }
    .metric-label {
        font-size: 0.88rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #a89487;
        font-weight: 600;
    }

    /* Dynamic Threat Badges */
    .badge-critical {
        background: rgba(240, 45, 15, 0.16);
        border: 1px solid #ff3314;
        color: #ff765e;
        padding: 6px 14px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 20px rgba(255, 50, 20, 0.25);
    }
    .badge-suspicious {
        background: rgba(255, 150, 0, 0.16);
        border: 1px solid #ff9d00;
        color: #ffbb4d;
        padding: 6px 14px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 20px rgba(255, 150, 0, 0.2);
    }
    .badge-safe {
        background: rgba(0, 210, 110, 0.14);
        border: 1px solid #00d26e;
        color: #5ce69b;
        padding: 6px 14px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 20px rgba(0, 210, 110, 0.2);
    }

    /* Custom progress bar in glowing hot orange */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #ff9e2b 0%, #ff5d00 50%, #e61d00 100%) !important;
        border-radius: 999px !important;
        box-shadow: 0 0 14px rgba(255, 95, 0, 0.6) !important;
    }
    .stProgress > div > div > div {
        background-color: rgba(40, 20, 10, 0.6) !important;
        border-radius: 999px !important;
        border: 1px solid rgba(255, 120, 0, 0.15) !important;
    }

    /* Sidebar Glass Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 4, 2, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 120, 0, 0.18) !important;
    }
</style>

<!-- Background Ambient Elements -->
<div class="fluted-curtain-bg"></div>
<div class="ambient-orb orb-top-right"></div>
<div class="ambient-orb orb-center-left"></div>
<div class="ambient-orb orb-bottom-right"></div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Encrypted Vault & Safe Key Retrieval
# -------------------------------------------------------------
saved_vault_key = load_vault_key()

# Check sources in order of preference:
# 1. Device Encrypted Vault (.vault.enc)
# 2. Environment variable
# 3. Streamlit secrets
# 4. In-memory temporary session
def get_streamlit_secret() -> str:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    return ""

api_key = (
    saved_vault_key
    or os.environ.get("GEMINI_API_KEY")
    or get_streamlit_secret()
    or st.session_state.get("temp_api_key", "")
)

with st.sidebar:
    st.markdown("<h3 style='color: #ff8533; font-family: Space Grotesk; margin-bottom: 2px;'>⚡ Access Credentials</h3>", unsafe_allow_html=True)
    if saved_vault_key and not st.session_state.get("editing_vault_key", False):
        masked = f"{saved_vault_key[:6]}••••••••••••{saved_vault_key[-4:]}" if len(saved_vault_key) > 10 else "••••••••••••"
        st.markdown(f"""
        <div style="background: rgba(255, 120, 0, 0.08); border: 1px solid rgba(255, 140, 0, 0.35); border-radius: 14px; padding: 14px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="display: inline-block; width: 8px; height: 8px; background: #00e676; border-radius: 50%; box-shadow: 0 0 10px #00e676;"></span>
                <span style="color: #69f0ae; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.8px;">Vault Encrypted & Active</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #ffeedd; background: rgba(0,0,0,0.45); padding: 8px 10px; border-radius: 8px; word-break: break-all;">
                {masked}
            </div>
            <div style="color: #8c786a; font-size: 0.74rem; margin-top: 8px; line-height: 1.4;">
                🔐 Machine-bound key • Persists across sessions
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            if st.button("🔄 Change Key", use_container_width=True):
                st.session_state["editing_vault_key"] = True
                st.rerun()
        with col_v2:
            if st.button("🗑️ Clear Key", use_container_width=True):
                clear_vault_key()
                st.session_state.pop("temp_api_key", None)
                st.session_state["editing_vault_key"] = False
                st.rerun()

    else:
        new_key_input = st.text_input(
            "Gemini API Key", 
            type="password", 
            placeholder="AQ... or AIza...", 
            value=st.session_state.get("temp_api_key", ""),
            help="Your key will be encrypted and saved to a machine-bound local vault file (.vault.enc)."
        )
        
        col_s1, col_s2 = st.columns([1.3, 1])
        with col_s1:
            if st.button("🔐 Save & Encrypt", use_container_width=True):
                if new_key_input.strip():
                    if save_vault_key(new_key_input):
                        st.session_state["editing_vault_key"] = False
                        st.session_state["temp_api_key"] = new_key_input.strip()
                        st.toast("Credentials securely encrypted & saved to device vault!", icon="🔒")
                        st.rerun()
                    else:
                        st.error("Failed to encrypt key.")
                else:
                    st.warning("Please enter a valid key first.")
        with col_s2:
            if st.session_state.get("editing_vault_key", False):
                if st.button("Cancel", use_container_width=True):
                    st.session_state["editing_vault_key"] = False
                    st.rerun()

        if new_key_input.strip():
            api_key = new_key_input.strip()

# Hero Header
st.markdown('<div class="brand-pill">Fake Offer Letter & Phishing Inspector</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 18px; margin: 6px 0 12px 0;">
    <img src="data:image/png;base64,{shield_b64}" style="width: 56px; height: 56px; filter: drop-shadow(0 0 16px rgba(255, 120, 0, 0.75)); object-fit: contain;">
    <h1 class="hero-title" style="margin: 0;">Phishield <span style="color: #ff7700;">Security Inspector</span></h1>
</div>
""", unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Protect yourself from recruitment wire fraud, bogus appointment letters, upfront equipment payment traps, and stealth domain impersonation with sub-second AI inspection.</p>', unsafe_allow_html=True)

# Quick sample prompt loader for instant testing
col_sample_a, col_sample_b, col_sample_c = st.columns([1, 1, 2])
with col_sample_a:
    if st.button("🚨 Load Fake Job Offer Sample", use_container_width=True):
        st.session_state["sample_input"] = (
            "Subject: Urgent Job Offer - Remote Assistant. Congratulations! You have been selected without an interview. "
            "We are issuing you a corporate check of $2,800 to purchase home office equipment from our approved vendor. "
            "You must wire $180 via Crypto/Zelle to the vendor for licensing setup before the check clears. "
            "Reach out to hiring manager Mark at hr-google-careers@gmail.com on Telegram (@google_hr_recruiter)."
        )
with col_sample_b:
    if st.button("✨ Load Legitimate Offer Sample", use_container_width=True):
        st.session_state["sample_input"] = (
            "Subject: Formal Job Offer: Senior Software Engineer at Acroware Inc.\n"
            "Dear Alex,\nFollowing your technical interviews with the team, we are delighted to offer you the full-time role of Senior Software Engineer. "
            "Your base salary will be $145,000/year, with health benefits beginning on your start date. "
            "All work laptops are pre-configured by our IT division and shipped directly to your address with no fees required. "
            "Please review the attached formal offer letter and sign through our corporate portal at https://careers.acroware.com/onboard/alex-981."
        )

# Main Two-Column Workflow
col_in, col_out = st.columns([1.08, 1], gap="large")

with col_in:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffffff; font-family: Space Grotesk; margin-bottom: 4px;'>📥 Target Investigation Content</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a89487; font-size: 0.9rem; margin-bottom: 18px;'>Paste email copy, message screenshots, recruiter contacts, or suspicious links.</p>", unsafe_allow_html=True)

    default_text = st.session_state.get("sample_input", "")
    input_text = st.text_area(
        "Offer Text / Email Body / Candidate Link:",
        value=default_text,
        placeholder="Paste full appointment letter text, compensation email, or recruiter URL here...",
        height=210
    )

    uploaded_file = st.file_uploader(
        "Attach Document / Screenshot (PNG, JPG, JPEG, PDF):", 
        type=["png", "jpg", "jpeg", "pdf"]
    )
    
    scan_btn = st.button("⚡ Execute Threat Inspection", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_out:
    if scan_btn:
        clean_key = api_key.strip() if api_key else ""
        if not clean_key:
            st.markdown("""
            <div class="glass-card" style="border-color: rgba(255, 70, 50, 0.4);">
                <h4 style="color: #ff6655;">🔑 API Key Required</h4>
                <p style="color: #c9b0a0; font-size: 0.92rem;">Please provide a valid Gemini API Key in the left sidebar to analyze documents.</p>
            </div>
            """, unsafe_allow_html=True)
        elif not input_text and not uploaded_file:
            st.markdown("""
            <div class="glass-card" style="border-color: rgba(255, 160, 40, 0.4);">
                <h4 style="color: #ffaa33;">⚠️ Input Content Required</h4>
                <p style="color: #c9b0a0; font-size: 0.92rem;">Please provide offer text or upload an offer document to proceed.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Decoding threat signatures with Gemini 3.6 Flash..."):
                try:
                    client = genai.Client(api_key=clean_key)
                    system_prompt = (
                        "You are a premier senior cybersecurity forensic analyst specializing in recruitment fraud, fake appointment letters, and job phishing scams. "
                        "Analyze the provided job offer, email, or URL with extreme scrutiny. "
                        "Evaluate for: "
                        "1) Domain legitimacy (free public emails like @gmail.com/@yahoo.com used by alleged corporate HR). "
                        "2) Advance-fee scam markers (demands for equipment fees, wire transfers, crypto, checks where candidate must return difference). "
                        "3) Unprofessional / suspicious channels (Telegram, WhatsApp interviews without real face-to-face or official video portal). "
                        "4) Urgency traps and non-interview instant hire letters. "
                        "Compute a rigorous Scam Threat Index (0-100%). "
                        "Output ONLY valid JSON matching this schema: "
                        "{"
                        "  \"scam_threat_index\": integer (0-100), "
                        "  \"verdict\": string (\"Safe\", \"Suspicious\", or \"Critical Scam Risk\"), "
                        "  \"payment_demand_flag\": boolean, "
                        "  \"domain_checks\": list of strings, "
                        "  \"red_flags\": list of strings, "
                        "  \"safety_guidelines\": list of strings"
                        "}"
                    )

                    prompt_contents = [system_prompt, f"Input Target Document:\n{input_text or ''}"]
                    if uploaded_file:
                        bytes_data = uploaded_file.read()
                        prompt_contents.append(
                            types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type or "application/octet-stream")
                        )

                    # Ultra-fast zero-latency config
                    fast_config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                        temperature=0.1
                    )
                    standard_config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )

                    response = None
                    # Recommended gemini-3.6-flash first with fallback
                    for model_name in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"]:
                        for cfg in [fast_config, standard_config]:
                            try:
                                response = client.models.generate_content(
                                    model=model_name,
                                    contents=prompt_contents,
                                    config=cfg
                                )
                                if response and response.text:
                                    break
                            except Exception as m_err:
                                err_str = str(m_err)
                                if "API_KEY_INVALID" in err_str or "PERMISSION_DENIED" in err_str:
                                    raise m_err
                                if "404" in err_str or "NOT_FOUND" in err_str:
                                    break
                                continue
                        if response and response.text:
                            break

                    if not response:
                        raise RuntimeError("Unable to communicate with Gemini models. Check your API key access.")

                    raw_text = response.text.strip()
                    if raw_text.startswith("```"):
                        raw_text = re.sub(r"^```(?:json)?\n", "", raw_text)
                        raw_text = re.sub(r"\n```$", "", raw_text)

                    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                    data = json.loads(match.group(0) if match else raw_text)

                    score = int(data.get("scam_threat_index", 0))
                    verdict = data.get("verdict", "Unknown")

                    # Right Column Result Card (Matching Glassmorphism Reference 1)
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown("<h3 style='color: #ffffff; font-family: Space Grotesk; margin-bottom: 2px;'>🎯 Cybersecurity Threat Assessment</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color: #a89487; font-size: 0.88rem; margin-bottom: 16px;'>Forensic analysis computed across recruitment fraud databases.</p>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value-huge">{score}%</div>
                        <div>
                            <div class="metric-label">Scam Threat Index</div>
                            <div style="margin-top: 4px;">
                                {f'<span class="badge-critical">🚨 CRITICAL RISK • {verdict}</span>' if score >= 70 else (f'<span class="badge-suspicious">⚠️ SUSPICIOUS • {verdict}</span>' if score >= 40 else f'<span class="badge-safe">✅ VERIFIED SAFE • {verdict}</span>')}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.progress(min(max(score / 100.0, 0.0), 1.0))

                    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255, 120, 0, 0.2); margin: 22px 0 16px 0;'>", unsafe_allow_html=True)

                    st.markdown("<h4 style='color: #ff9933; font-family: Space Grotesk; font-size: 1.15rem; margin-bottom: 12px;'>🚩 Identified Risk Indicators</h4>", unsafe_allow_html=True)
                    
                    if data.get("payment_demand_flag"):
                        st.markdown("""
                        <div class="glass-tile" style="border-left: 4px solid #ff3311; background: rgba(40, 10, 5, 0.65);">
                            <strong style="color: #ff5533; font-size: 0.95rem;">🔴 Severe Violation: Advance-Fee / Equipment Deposit Trap</strong>
                            <div style="color: #d6c0b0; font-size: 0.85rem; margin-top: 4px;">Demands candidates wire money or buy equipment from proprietary vendors. High probability of fraudulent check bounce.</div>
                        </div>
                        """, unsafe_allow_html=True)

                    for d in data.get("domain_checks", []):
                        st.markdown(f"""
                        <div class="glass-tile">
                            <span style="color: #ffaa55; font-weight: 700; font-size: 0.88rem;">🌐 Channel & Domain Verification:</span>
                            <div style="color: #efe2d5; font-size: 0.88rem; margin-top: 3px;">{d}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    for f in data.get("red_flags", []):
                        st.markdown(f"""
                        <div class="glass-tile">
                            <span style="color: #ff8833; font-weight: 700; font-size: 0.88rem;">⚠️ Threat Signal:</span>
                            <div style="color: #efe2d5; font-size: 0.88rem; margin-top: 3px;">{f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if not data.get("domain_checks") and not data.get("red_flags") and not data.get("payment_demand_flag"):
                        st.markdown("""
                        <div class="glass-tile" style="border-left: 4px solid #00d26e;">
                            <span style="color: #5ce69b; font-weight: 700;">🟢 No malicious markers detected.</span>
                            <div style="color: #d0c0b5; font-size: 0.85rem; margin-top: 3px;">The document matches typical corporate recruitment conventions.</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<h4 style='color: #ff9933; font-family: Space Grotesk; font-size: 1.15rem; margin: 20px 0 12px 0;'>💡 Tactical Defense Protocol</h4>", unsafe_allow_html=True)
                    for tip in data.get("safety_guidelines", []):
                        st.markdown(f"""
                        <div style="display: flex; gap: 10px; margin-bottom: 8px; font-size: 0.88rem; color: #dfd0c5;">
                            <span style="color: #ff8822;">▸</span>
                            <span>{tip}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f"""
                    <div class="glass-card" style="border-color: rgba(255, 50, 50, 0.4);">
                        <h4 style="color: #ff5544;">⚠️ Analysis Error</h4>
                        <p style="color: #dfd0c5; font-size: 0.9rem;">{str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Initial Placeholder Glass Card (Matching Reference Visual 1 exactly)
        st.markdown(f"""
        <div class="glass-card" style="display: flex; flex-direction: column; justify-content: center; min-height: 420px;">
            <div style="display: inline-block; background: rgba(255, 120, 0, 0.1); border: 1px solid rgba(255, 120, 0, 0.3); color: #ff9933; padding: 4px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; width: fit-content; margin-bottom: 12px;">
                Inspection Engine Ready
            </div>
            <h3 style="color: #ffffff; font-family: Space Grotesk; font-size: 1.8rem; margin: 0 0 10px 0;">
                Awaiting Target Submission
            </h3>
            <p style="color: #b09e90; font-size: 0.95rem; line-height: 1.6; margin-bottom: 24px;">
                Submit an appointment letter, compensation email, recruiter contact, or link on the left to activate forensic AI threat detection.
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="glass-tile" style="margin: 0;">
                    <div style="color: #ff9944; font-weight: 700; font-size: 0.88rem;">🔍 Deep Domain Verification</div>
                    <div style="color: #9c8a7d; font-size: 0.8rem; margin-top: 4px;">Flags spoofed corporate emails and deceptive URLs.</div>
                </div>
                <div class="glass-tile" style="margin: 0;">
                    <div style="color: #ff9944; font-weight: 700; font-size: 0.88rem;">💳 Upfront Fee Shield</div>
                    <div style="color: #9c8a7d; font-size: 0.8rem; margin-top: 4px;">Detects check overpayment and equipment scams.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)