
import streamlit as st
import subprocess
import os
import time
import threading
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Local TinyLlama Chat", 
    page_icon="🦙", 
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2e7bcf;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    .user-message {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        margin-left: 20%;
    }
    .assistant-message {
        background: #e8f4f8;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        margin-right: 20%;
        border-left: 4px solid #2e7bcf;
    }
    .status-indicator {
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-bottom: 10px;
    }
    .status-ready { background: #d4edda; color: #155724; }
    .status-error { background: #f8d7da; color: #721c24; }
    .status-loading { background: #fff3cd; color: #856404; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "model_status" not in st.session_state:
    st.session_state.model_status = "checking"
if "model_path" not in st.session_state:
    st.session_state.model_path = ""
if "binary_path" not in st.session_state:
    st.session_state.binary_path = ""
