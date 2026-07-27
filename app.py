import os
import time
import streamlit as st
from dotenv import load_dotenv

from src.document_parser import parse_all_uploaded_files
from src.rag_engine import RAGEngine
from src.ai_generator import generate_notes_for_single_unit, clear_user_doubt
from src.pdf_generator import build_single_combined_pdf

load_dotenv()

st.set_page_config(
    page_title="Inkscribe AI - Smart Exam Notes Generator",
    page_icon="✍️",
    layout="wide"
)

# Session State Initialization
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "generated_notes_dict" not in st.session_state:
    st.session_state.generated_notes_dict = {}
if "pdf_path_dict" not in st.session_state:
    st.session_state.pdf_path_dict = {}
if "is_completed" not in st.session_state:
    st.session_state.is_completed = False

# API Key Priority
system_key = os.getenv("GROQ_API_KEY", "")
active_api_key = st.session_state.user_api_key.strip() if st.session_state.user_api_key.strip() else system_key

st.markdown("""
<style>
    /* Hide Default Header */
    header[data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* Background Styling */
    .stApp { 
        background: radial-gradient(circle at 50% 0%, #0a192f 0%, #060c1a 60%, #02060e 100%) !important; 
        color: #f8fafc !important; 
    }
    p, span, label, div[data-testid="stMarkdownContainer"] { color: #e2e8f0 !important; }
    
    /* Gold Glow Title & Headings */
    .gold-title { 
        color: #fbbf24 !important; 
        font-size: 3.5rem !important; 
        font-weight: 800 !important; 
        text-align: center !important; 
        text-shadow: 0 0 35px rgba(251, 191, 36, 0.6) !important; 
        margin-bottom: 4px !important; 
    }
    .gold-glow-heading {
        color: #fbbf24 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 25px rgba(251, 191, 36, 0.7) !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* File Upload Box - Interactive Purple Glow on Click/Hover */
    div[data-testid="stFileUploader"] { 
        background: rgba(10, 25, 47, 0.7) !important; 
        border: 2px solid rgba(168, 85, 247, 0.35) !important; 
        border-radius: 16px !important; 
        padding: 16px !important; 
        transition: all 0.3s ease-in-out !important;
    }
    div[data-testid="stFileUploader"]:hover, 
    div[data-testid="stFileUploader"]:focus-within { 
        border-color: #a855f7 !important; 
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.8) !important; 
        background: rgba(15, 23, 42, 0.9) !important; 
    }

    /* Text Input Box - Interactive Purple Glow on Click/Hover */
    div[data-testid="stTextInput"] input { 
        background: rgba(10, 25, 47, 0.8) !important; 
        border: 2px solid rgba(168, 85, 247, 0.35) !important; 
        color: #f8fafc !important; 
        border-radius: 12px !important; 
        padding: 12px 16px !important;
        transition: all 0.3s ease-in-out !important;
    }
    div[data-testid="stTextInput"] input:focus, 
    div[data-testid="stTextInput"] input:hover { 
        border-color: #a855f7 !important; 
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.8) !important; 
        background: rgba(15, 23, 42, 0.95) !important; 
    }

    /* Primary Button Styling */
    div.stButton > button { 
        background: linear-gradient(135deg, #b45309 0%, #d97706 50%, #f59e0b 100%) !important; 
        color: #030712 !important; 
        border-radius: 12px !important; 
        padding: 16px 28px !important; 
        font-weight: 800 !important; 
        font-size: 18px !important; 
        border: none !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { 
        background: linear-gradient(135deg, #15803d 0%, #16a34a 50%, #22c55e 100%) !important; 
        color: #ffffff !important; 
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

@st.dialog("🚨 Groq API Key Required")
def show_api_limit_popup():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #064e3b 100%); padding: 20px; border-radius: 16px; border: 2px solid #a855f7; text-align: center;">
        <h2 style="color: #4ade80 !important; font-size: 1.6rem; margin-bottom: 8px;">⚡ Groq API Key Required</h2>
        <p style="color: #f3e8ff !important;">Please enter a valid Groq API Key to proceed!</p>
        <a href="https://console.groq.com/keys" target="_blank" style="background: #22c55e; color: #000; padding: 10px 20px; border-radius: 10px; text-decoration: none; font-weight: 800;">Get Free Groq Key</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    new_key_input = st.text_input("Paste your Groq API Key here:", type="password", placeholder="gsk_...")
    if st.button("🚀 Save Key & Continue"):
        if new_key_input.strip():
            st.session_state.user_api_key = new_key_input.strip()
            st.success("API Key saved!")
            st.rerun()

st.markdown("""
<div style="text-align: center; padding: 5px 0px 20px 0px;">
    <h1 class="gold-title">✍️ Inkscribe AI</h1>
    <p style="color: #cbd5e1 !important; font-size: 1.2rem;">Single-Click Exam Notes & PDF Generator ⚡</p>
</div>
""", unsafe_allow_html=True)

# 1. Upload Section
st.markdown('<div class="gold-glow-heading">1. Upload Study Materials</div>', unsafe_allow_html=True)

u_col1, u_col2 = st.columns(2)

with u_col1:
    syllabus_files = st.file_uploader("📄 Upload PDF Syllabus & Question Papers", type=['pdf'], accept_multiple_files=True)
with u_col2:
    other_files = st.file_uploader("📦 Upload Textbooks, PPTs or ZIPs", type=['pdf', 'pptx', 'ppt', 'zip'], accept_multiple_files=True)

st.markdown("<br>", unsafe_allow_html=True)

# Single-Click Button
if st.button("🚀 GENERATE ALL 5 UNITS NOTES & PDFs (SINGLE CLICK)", use_container_width=True):
    all_uploads = (syllabus_files or []) + (other_files or [])
    
    if not all_uploads:
        st.error("Please upload at least one study material above before generating!")
    elif not active_api_key:
        show_api_limit_popup()
    else:
        try:
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            status_text.markdown("### 🔍 Indexing Uploaded Materials...")
            parsed_docs = parse_all_uploaded_files(all_uploads)
            st.session_state.rag_engine = RAGEngine()
            st.session_state.rag_engine.add_documents(parsed_docs)
            progress_bar.progress(15)

            st.session_state.generated_notes_dict = {}
            st.session_state.pdf_path_dict = {}

            for unit_num in range(1, 6):
                status_text.markdown(f"### ⚡ Generating Unit {unit_num} of 5 (2M & 16M Notes + PDF)...")
                
                unit_notes = generate_notes_for_single_unit(
                    api_key=active_api_key,
                    rag_engine=st.session_state.rag_engine,
                    unit_number=unit_num
                )

                pdf_filename = f"Inkscribe_Unit_{unit_num}_Exam_Notes.pdf"
                pdf_path = build_single_combined_pdf(unit_notes, output_filename=pdf_filename)

                st.session_state.generated_notes_dict[unit_num] = unit_notes
                st.session_state.pdf_path_dict[unit_num] = pdf_path

                progress_bar.progress(15 + (unit_num * 17))
                time.sleep(1.5)

            st.session_state.is_completed = True
            status_text.markdown("### 🎉 All 5 Units Successfully Generated!")
            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            show_api_limit_popup()

if st.session_state.is_completed and st.session_state.pdf_path_dict:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="gold-glow-heading">📥 Download Generated Unit PDFs</div>', unsafe_allow_html=True)
    
    d_cols = st.columns(5)
    for idx, unit_num in enumerate(range(1, 6)):
        with d_cols[idx]:
            pdf_path = st.session_state.pdf_path_dict.get(unit_num, "")
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download Unit {unit_num}",
                        data=f,
                        file_name=f"Inkscribe_Unit_{unit_num}_Notes.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="gold-glow-heading">📄 Preview Notes</div>', unsafe_allow_html=True)
    for unit_num in range(1, 6):
        with st.expander(f"Unit {unit_num} Notes Content"):
            st.markdown(st.session_state.generated_notes_dict.get(unit_num, ""))

st.markdown("---")

# 2. Doubt Tutor Section
st.markdown('<div class="gold-glow-heading">🤖 Interactive AI Doubt Tutor</div>', unsafe_allow_html=True)

user_doubt = st.text_input("Ask your doubt question here:", placeholder="e.g., Explain step 2 of Unit 1...")

if st.button("💡 Clear Doubt", use_container_width=True):
    if not active_api_key:
        show_api_limit_popup()
    elif not user_doubt.strip():
        st.warning("Please type your question first!")
    else:
        try:
            with st.spinner("Analyzing doubt..."):
                notes_ctx = "\n".join(st.session_state.generated_notes_dict.values()) if st.session_state.generated_notes_dict else ""
                explanation = clear_user_doubt(active_api_key, user_doubt, notes_ctx)
                st.success("### 💡 Explanation:")
                st.markdown(explanation)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            show_api_limit_popup()
