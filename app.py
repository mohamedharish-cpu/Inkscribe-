import os
import streamlit as st
from dotenv import load_dotenv

from src.document_parser import parse_all_uploaded_files
from src.rag_engine import RAGEngine
from src.ai_generator import generate_exam_notes_for_unit, clear_user_doubt
from src.pdf_generator import build_single_combined_pdf

load_dotenv()

st.set_page_config(
    page_title="Inkscribe AI - Smart Exam Notes Generator",
    page_icon="✍️",
    layout="wide"
)

# Initialize Session State for User Key
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""

# API Key Priority: Session State (User Key from Popup) > .env (System Key)
system_key = os.getenv("GEMINI_API_KEY", "")
active_api_key = st.session_state.user_api_key.strip() if st.session_state.user_api_key.strip() else system_key

# -------------------------------------------------------------
# LUXURIOUS SAPPHIRE, VIOLET GLOW & GREEN ACCENT THEME (CUSTOM CSS)
# -------------------------------------------------------------
st.markdown("""
<style>
    /* 0. HIDE DEFAULT STREAMLIT HEADER & REMOVE TOP GAP */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* 1. Deep Sapphire Royal Background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0a192f 0%, #060c1a 60%, #02060e 100%) !important;
        color: #f8fafc !important;
    }

    /* 2. Global Text & Markdown Colors */
    p, span, label, div[data-testid="stMarkdownContainer"] {
        color: #e2e8f0 !important;
    }

    /* 3. STRICT GOLD FOR MAIN TITLE (h1) & SUBHEADERS */
    .stApp h1, .gold-title {
        color: #fbbf24 !important;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        letter-spacing: 1px !important;
        text-shadow: 0 0 35px rgba(251, 191, 36, 0.5) !important;
        margin-bottom: 4px !important;
    }

    /* SECTION A & B HEADERS (EMERALD GREEN STYLING) */
    .green-section-header {
        color: #22c55e !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 0 15px rgba(34, 197, 94, 0.4) !important;
        margin-top: 15px !important;
        margin-bottom: 15px !important;
        display: inline-block;
        transition: all 0.3s ease !important;
    }

    h2, h3 {
        color: #fbbf24 !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
    }

    /* 4. Sidebar - Royal Navy Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(6, 12, 26, 0.95) !important;
        border-right: 1px solid rgba(168, 85, 247, 0.3) !important;
        backdrop-filter: blur(20px) !important;
    }

    /* 5. Uploader Section Labels (Warm Gold) */
    div[data-testid="stFileUploader"] label p {
        color: #f59e0b !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        letter-spacing: 0.4px !important;
    }

    /* 6. GLASS CARDS FOR UPLOADERS + VIOLET ELECTRIC GLOW */
    div[data-testid="stFileUploader"] {
        background: rgba(10, 25, 47, 0.7) !important;
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* VIOLET GLOW HOVER & ACTIVE STATE FOR FILE UPLOADERS */
    div[data-testid="stFileUploader"]:hover,
    div[data-testid="stFileUploader"]:focus-within {
        border-color: #a855f7 !important;
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.6) !important;
        transform: translateY(-3px) !important;
    }

    /* FIX DROPZONE INSIDE UPLOADER (SOLID NAVY BACKGROUND & CLEAR TEXT) */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #0f172a !important;
        border: 1px dashed #a855f7 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    section[data-testid="stFileUploaderDropzone"] span, 
    section[data-testid="stFileUploaderDropzone"] div,
    section[data-testid="stFileUploaderDropzone"] small {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    /* Uploader Browse Button Styling (Vibrant Purple) */
    section[data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 16px !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: #22c55e !important;
        color: #000000 !important;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.7) !important;
    }

    /* 7. TEXT INPUT BOX (AI TUTOR & POPUP) WITH VIOLET GLOW */
    div[data-baseweb="input"] {
        background-color: #0f172a !important;
        border: 1px solid rgba(168, 85, 247, 0.5) !important;
        border-radius: 10px !important;
        padding: 4px 8px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #a855f7 !important;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.7) !important;
    }

    div[data-baseweb="input"] input {
        color: #ffffff !important;
        background-color: transparent !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }

    ::placeholder {
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }

    /* 8. ROYAL GOLD GENERATE BUTTON WITH GREEN ACCENT */
    div.stButton > button {
        background: linear-gradient(135deg, #b45309 0%, #d97706 50%, #f59e0b 100%) !important;
        color: #030712 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 16px 32px !important;
        font-weight: 800 !important;
        font-size: 18px !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 8px 25px rgba(217, 119, 6, 0.4) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #15803d 0%, #16a34a 50%, #22c55e 100%) !important;
        color: #ffffff !important;
        border-color: #22c55e !important;
        box-shadow: 0 12px 35px rgba(34, 197, 94, 0.6) !important;
        transform: translateY(-2px) scale(1.005) !important;
    }

    hr {
        border-color: rgba(168, 85, 247, 0.25) !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SMART POPUP DIALOG (WITH DIRECT API INPUT INSIDE POPUP)
# -------------------------------------------------------------
@st.dialog("🚨 Access Limit Reached!")
def show_api_limit_popup():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #064e3b 100%); padding: 20px; border-radius: 16px; border: 2px solid #a855f7; text-align: center; box-shadow: 0 0 35px rgba(168, 85, 247, 0.5);">
        <h2 style="color: #4ade80 !important; font-size: 1.6rem; margin-bottom: 8px; font-weight: 800;">🔑 Access Limit Exhausted</h2>
        <p style="color: #f3e8ff !important; font-size: 0.98rem; line-height: 1.4;">
            The active API Key limit is exhausted. Create a free key from Google AI Studio & paste it below:
        </p>
        <a href="https://aistudio.google.com/app/apikey" target="_blank" style="background: linear-gradient(135deg, #a855f7 0%, #22c55e 100%); color: #000000; padding: 10px 20px; border-radius: 10px; text-decoration: none; font-weight: 800; font-size: 0.95rem; display: inline-block; margin-top: 10px; margin-bottom: 15px; box-shadow: 0 0 20px rgba(34, 197, 94, 0.5);">
            ✨ Get Free Gemini API Key
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    new_key_input = st.text_input("Paste your new Gemini API Key here:", type="password", placeholder="AIzaSy...")
    
    if st.button("🚀 Save Key & Continue Access", use_container_width=True):
        if new_key_input.strip():
            st.session_state.user_api_key = new_key_input.strip()
            st.success("API Key saved successfully! Resuming...")
            st.rerun()
        else:
            st.warning("Please paste a valid API key!")

# Initialize Session State
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "generated_notes" not in st.session_state:
    st.session_state.generated_notes = ""
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

# -------------------------------------------------------------
# CENTERED PREMIUM GOLD TITLE HEADER
# -------------------------------------------------------------
st.markdown("""
<div style="text-align: center; padding: 5px 0px 20px 0px;">
    <h1 class="gold-title">✍️ Inkscribe AI</h1>
    <p style="color: #cbd5e1 !important; font-size: 1.2rem; font-weight: 500; letter-spacing: 0.5px; margin-top: 5px;">
        Automated Exam-Ready Handwritten Notes Generator & Interactive AI Tutor
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# MAIN DASHBOARD: Categorized Upload Sections
# -------------------------------------------------------------
st.header("1. Upload Study Materials")

# --- SECTION A: PDF DOCUMENTS ---
st.markdown('<div class="green-section-header">📄 Section A: PDF Documents</div>', unsafe_allow_html=True)
pdf_col1, pdf_col2 = st.columns(2)

with pdf_col1:
    syllabus_files = st.file_uploader("📄 Upload your PDF Syllabus & Specs", type=['pdf'], accept_multiple_files=True)
    pyq_files = st.file_uploader("📄 Upload your PDF Question Papers (PYQs)", type=['pdf'], accept_multiple_files=True)

with pdf_col2:
    textbook_files = st.file_uploader("📄 Upload your PDF Textbooks & Reference Notes", type=['pdf'], accept_multiple_files=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- SECTION B: PPT & ZIP ARCHIVES ---
st.markdown('<div class="green-section-header">📦 Section B: Presentations & Zip Archives</div>', unsafe_allow_html=True)
media_col1, media_col2 = st.columns(2)

with media_col1:
    ppt_files = st.file_uploader("📦 Upload your PPT / PPTX Lecture Slides", type=['pptx', 'ppt'], accept_multiple_files=True)

with media_col2:
    zip_files = st.file_uploader("📦 Upload your ZIP Study Material Packs", type=['zip'], accept_multiple_files=True)

st.markdown("---")

# -------------------------------------------------------------
# GENERATION ENGINE PIPELINE
# -------------------------------------------------------------
if st.button("📄 Generate Single Combined Handwritten PDF Notes", use_container_width=True):
    if not active_api_key:
        show_api_limit_popup()
    else:
        all_uploads = []
        for file_list in [syllabus_files, pyq_files, textbook_files, ppt_files, zip_files]:
            if file_list:
                all_uploads.extend(file_list)

        if not all_uploads:
            st.error("Please upload at least one study material (PDF, PPTX, or ZIP) to proceed!")
        else:
            try:
                with st.spinner("Step 1/3: Extracting text from uploaded PDFs, PPTs, and ZIP packs..."):
                    parsed_docs = parse_all_uploaded_files(all_uploads)

                with st.spinner("Step 2/3: Indexing documents into ChromaDB Vector Search..."):
                    st.session_state.rag_engine = RAGEngine()
                    num_chunks = st.session_state.rag_engine.add_documents(parsed_docs)
                    st.success(f"Successfully processed and indexed {num_chunks} document chunks!")

                with st.spinner("Step 3/3: AI generating step-by-step derivations & color-coded notes..."):
                    context = st.session_state.rag_engine.query_context("All Units Core Concepts", top_k=10)
                    
                    notes = generate_exam_notes_for_unit(
                        api_key=active_api_key,
                        unit_name="Complete Syllabus High-Yield Notes",
                        context=context,
                        mode="🏆 Topper Mode (90%+ Distinction)"
                    )
                    st.session_state.generated_notes = notes

                    # Build Single Combined PDF
                    pdf_file_path = build_single_combined_pdf(notes)
                    st.session_state.pdf_path = pdf_file_path

                st.balloons()
            except Exception as e:
                show_api_limit_popup()

# -------------------------------------------------------------
# DISPLAY RESULTS & PDF DOWNLOAD
# -------------------------------------------------------------
if st.session_state.generated_notes:
    st.markdown("---")
    st.header("2. Exam Notes Preview & PDF Download")

    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        with open(st.session_state.pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Single Combined Handwritten PDF Notes",
                data=pdf_file,
                file_name="Inkscribe_Exam_Handwritten_Notes.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    with st.expander("📄 Click to View Generated Color-Coded Markdown Notes", expanded=True):
        st.markdown(st.session_state.generated_notes)

# -------------------------------------------------------------
# 🤖 INTERACTIVE AI DOUBT CLEARING TUTOR (VIOLET GLOW)
# -------------------------------------------------------------
st.markdown("---")
st.header("2. 🤖 Interactive AI Doubt Tutor")
st.caption("Have doubts on any topic, derivation, or formula? Type your question below and Inkscribe AI will explain it step-by-step!")

user_doubt = st.text_input("Ask your doubt question here:", placeholder="e.g., Explain step 2 of the derivation or give a real-world analogy...")

if st.button("💡 Explain & Clear My Doubt", use_container_width=True):
    if not active_api_key:
        show_api_limit_popup()
    elif not user_doubt.strip():
        st.warning("Please type your doubt question above first!")
    else:
        try:
            with st.spinner("Inkscribe AI Tutor is breaking down the solution for you..."):
                context_to_use = st.session_state.generated_notes if st.session_state.generated_notes else "General Engineering / Academic Syllabus Doubt"
                explanation = clear_user_doubt(
                    api_key=active_api_key,
                    user_question=user_doubt,
                    notes_context=context_to_use
                )
                st.success("### 💡 AI Tutor Explanation:")
                st.markdown(explanation)
        except Exception as e:
            show_api_limit_popup()