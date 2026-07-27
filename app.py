import os
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

# Initialize Session States
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "current_unit" not in st.session_state:
    st.session_state.current_unit = 1
if "generated_notes_dict" not in st.session_state:
    st.session_state.generated_notes_dict = {}
if "pdf_path_dict" not in st.session_state:
    st.session_state.pdf_path_dict = {}

# API Key Priority
system_key = os.getenv("GROQ_API_KEY", "")
active_api_key = st.session_state.user_api_key.strip() if st.session_state.user_api_key.strip() else system_key

# Styling
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    .stApp { background: radial-gradient(circle at 50% 0%, #0a192f 0%, #060c1a 60%, #02060e 100%) !important; color: #f8fafc !important; }
    p, span, label, div[data-testid="stMarkdownContainer"] { color: #e2e8f0 !important; }
    .stApp h1, .gold-title { color: #fbbf24 !important; font-size: 3.5rem !important; font-weight: 800 !important; text-align: center !important; text-shadow: 0 0 35px rgba(251, 191, 36, 0.5) !important; margin-bottom: 4px !important; }
    .green-section-header { color: #22c55e !important; font-size: 1.6rem !important; font-weight: 800 !important; text-shadow: 0 0 15px rgba(34, 197, 94, 0.4) !important; margin: 15px 0 !important; display: inline-block; }
    h2, h3 { color: #fbbf24 !important; font-weight: 700 !important; }
    div[data-testid="stFileUploader"] { background: rgba(10, 25, 47, 0.7) !important; border: 1px solid rgba(168, 85, 247, 0.35) !important; border-radius: 16px !important; padding: 16px !important; }
    div.stButton > button { background: linear-gradient(135deg, #b45309 0%, #d97706 50%, #f59e0b 100%) !important; color: #030712 !important; border-radius: 12px !important; padding: 14px 28px !important; font-weight: 800 !important; font-size: 16px !important; }
    div.stButton > button:hover { background: linear-gradient(135deg, #15803d 0%, #16a34a 50%, #22c55e 100%) !important; color: #ffffff !important; }
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

# Header
st.markdown("""
<div style="text-align: center; padding: 5px 0px 20px 0px;">
    <h1 class="gold-title">✍️ Inkscribe AI</h1>
    <p style="color: #cbd5e1 !important; font-size: 1.2rem;">Automated High-Yield Exam Notes Generator ⚡</p>
</div>
""", unsafe_allow_html=True)

# 1. File Upload Section
st.header("1. Upload Study Materials")
u_col1, u_col2 = st.columns(2)

with u_col1:
    syllabus_files = st.file_uploader("📄 Upload PDF Syllabus & Question Papers", type=['pdf'], accept_multiple_files=True)
with u_col2:
    other_files = st.file_uploader("📦 Upload Textbooks, PPTs or ZIPs", type=['pdf', 'pptx', 'ppt', 'zip'], accept_multiple_files=True)

if st.button("🔍 Process & Index Uploaded Documents", use_container_width=True):
    all_uploads = (syllabus_files or []) + (other_files or [])
    if not all_uploads:
        st.error("Please upload at least one file first!")
    else:
        with st.spinner("Processing uploaded files..."):
            parsed_docs = parse_all_uploaded_files(all_uploads)
            st.session_state.rag_engine = RAGEngine()
            num_chunks = st.session_state.rag_engine.add_documents(parsed_docs)
            st.session_state.current_unit = 1  # Reset to Unit 1
            st.success(f"Successfully processed & indexed {num_chunks} content chunks!")

st.markdown("---")

# 2. Sequential Unit Generation Section
st.header("2. Exam Notes Generation Flow")

if st.session_state.rag_engine is None:
    st.info("💡 Please upload study materials above and click 'Process & Index Uploaded Documents' to start!")
else:
    unit_num = st.session_state.current_unit
    
    # Progress Header
    st.markdown(f"### 📌 Current Step: **Unit {unit_num} of 5**")

    # Check if current unit is already generated
    if unit_num in st.session_state.generated_notes_dict:
        st.success(f"✅ Unit {unit_num} Notes & PDF are Ready!")

        # Download Button
        pdf_path = st.session_state.pdf_path_dict[unit_num]
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label=f"📥 Download Unit {unit_num} PDF Notes",
                    data=f,
                    file_name=f"Inkscribe_Unit_{unit_num}_Notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        # Expandable Preview
        with st.expander(f"📄 View Unit {unit_num} Generated Notes Preview", expanded=False):
            st.markdown(st.session_state.generated_notes_dict[unit_num])

        st.markdown("<br>", unsafe_allow_html=True)

        # NEXT BUTTON logic
        if unit_num < 5:
            if st.button(f"➡️ Proceed to Unit {unit_num + 1} (Next)", use_container_width=True):
                st.session_state.current_unit += 1
                st.rerun()
        else:
            st.balloons()
            st.success("🎉 All 5 Units successfully generated! All PDF downloads are complete.")
            if st.button("🔄 Start Over / Regenerate Unit 1", use_container_width=True):
                st.session_state.current_unit = 1
                st.rerun()

    else:
        # Generate Button for Current Unit
        if st.button(f"🚀 Generate Unit {unit_num} Notes & PDF", use_container_width=True):
            if not active_api_key:
                show_api_limit_popup()
            else:
                try:
                    with st.spinner(f"Generating Unit {unit_num} Notes (7-10 Two-Marks & 5-7 Sixteen-Marks)..."):
                        unit_notes = generate_notes_for_single_unit(
                            api_key=active_api_key,
                            rag_engine=st.session_state.rag_engine,
                            unit_number=unit_num
                        )

                        pdf_filename = f"Inkscribe_Unit_{unit_num}_Exam_Notes.pdf"
                        pdf_path = build_single_combined_pdf(unit_notes, output_filename=pdf_filename)

                        st.session_state.generated_notes_dict[unit_num] = unit_notes
                        st.session_state.pdf_path_dict[unit_num] = pdf_path
                        st.rerun()
                except Exception as e:
                    st.error(f"Error occurred: {str(e)}")
                    show_api_limit_popup()

st.markdown("---")

# 3. AI Doubt Tutor
st.header("3. 🤖 Interactive AI Doubt Tutor")
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
