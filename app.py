import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from qa.chat import answer

# Page config
st.set_page_config(
    page_title="I-MED Radiology Assistant",
    page_icon="🏥",
    layout="centered"
)

# Header
st.markdown("""
    <div style='text-align: center; padding: 20px 0'>
        <h1 style='color: #003087'>🏥 I-MED Radiology Assistant</h1>
        <p style='color: #666; font-size: 16px'>Ask questions about radiology procedures at I-MED Radiology Network</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Example questions
st.markdown("#### 💡 Try asking:")
cols = st.columns(2)
examples = [
    "What happens during an MRI scan?",
    "Do I need to fast before a CT scan?",
    "How do I prepare for an ultrasound?",
    "Does Medicare cover X-ray?",
    "How long does a mammography take?",
    "What are the risks of an X-ray?",
]
for i, example in enumerate(examples):
    with cols[i % 2]:
        if st.button(example, use_container_width=True):
            st.session_state.query = example

st.divider()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
query = st.chat_input("Ask a question about I-MED procedures...")

# Handle example button clicks
if "query" in st.session_state and st.session_state.query:
    query = st.session_state.query
    st.session_state.query = None

if query:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("Searching I-MED procedures..."):
            response = answer(query)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px'>
        Answers are grounded in content scraped from i-med.com.au. 
        Always consult your doctor or I-MED directly for medical advice.
    </div>
""", unsafe_allow_html=True)