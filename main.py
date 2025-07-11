import streamlit as st
from llama_cpp import Llama
import os

# Page configuration
st.set_page_config(
    page_title="Skilvyn - AI Learning Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load local TinyLlama model
MODEL_PATH = os.path.expanduser("~/llama.cpp/models/TinyLlama/tinyllama-1.1b-chat-v1.0.Q2_K.gguf")
llm = Llama(model_path=MODEL_PATH, n_threads=4)

# Initialize session state defaults
def init_defaults():
    defaults = {
        "chat_history": [],
        "user_info": {},
        "learning_path": [],
        "current_step": 0,
        "stage": "welcome",
        "max_history": 20
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_defaults()

# Cached learning path template
@st.cache_data
def get_learning_path_template():
    return [
        {"title": "Introduction to Prompt Engineering", "welcome": "Welcome to your journey!"},
        {"title": "Writing Effective Prompts", "welcome": "Let's write better prompts!"},
        {"title": "Using Context in Prompts", "welcome": "Context matters!"},
        {"title": "Advanced Techniques", "welcome": "Time for advanced methods."},
        {"title": "Practical Projects", "welcome": "Let's build something!"}
    ]

# Trim chat history
def trim_history():
    history = st.session_state.chat_history
    if len(history) > st.session_state.max_history:
        st.session_state.chat_history = history[-st.session_state.max_history:]

# Generate response using Llama model
def generate_response(prompt: str) -> str:
    resp = llm.create_completion(
        prompt=prompt,
        max_tokens=512,
        temperature=0.7
    )
    return resp.choices[0].text.strip()

# Display chat messages
def show_chat():
    for msg in st.session_state.chat_history:
        tag = "🤖" if msg['role']=='assistant' else "👤"
        align = 'left' if msg['role']=='assistant' else 'right'
        st.markdown(f"<div style='text-align:{align}; padding:8px;'><b>{tag}</b> {msg['content']}</div>", unsafe_allow_html=True)

# Main App Title
st.title("🎓 Skilvyn")

# Onboarding: get user name
if st.session_state.stage == 'welcome':
    name = st.text_input("Welcome! What's your name?")
    if name:
        st.session_state.user_info['name'] = name
        st.session_state.chat_history.append({'role':'user','content':name})
        greeting = f"Hello {name}! Please enter your skill level (Beginner/Intermediate/Advanced)."
        st.session_state.chat_history.append({'role':'assistant','content':greeting})
        st.session_state.stage = 'ask_level'
    show_chat()
    st.stop()

# Ask skill level and generate path
if st.session_state.stage == 'ask_level':
    level = st.text_input("Your skill level?")
    if level:
        st.session_state.user_info['level'] = level
        st.session_state.chat_history.append({'role':'user','content':level})
        # Generate learning path
        path = get_learning_path_template()
        st.session_state.learning_path = path
        welcome = path[0]['welcome']
        st.session_state.chat_history.append({'role':'assistant','content':welcome})
        st.session_state.stage = 'in_session'
    show_chat()
    st.stop()

# Main chat loop
if st.session_state.stage == 'in_session':
    show_chat()
    prompt = st.text_input("Ask a question or proceed...")
    if prompt:
        st.session_state.chat_history.append({'role':'user','content':prompt})
        current = st.session_state.learning_path[st.session_state.current_step]
        system_prompt = f"You are an AI tutor for the unit: {current['title']}"
        full_prompt = system_prompt + "\nUser: " + prompt
        try:
            answer = generate_response(full_prompt)
            st.session_state.chat_history.append({'role':'assistant','content':answer})
            trim_history()
        except Exception as e:
            st.error(f"Error: {e}")
    st.stop()

# Completion
st.success("🎉 Congratulations! You've completed all learning units.")

