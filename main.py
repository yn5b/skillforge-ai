
import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Skilvyn - AI Learning Tutor", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2e7bcf;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
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
    .learning-path {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
    .unit-card {
        background: white;
        color: #333;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .progress-bar {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        height: 8px;
        margin: 10px 0;
    }
    .progress-fill {
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        height: 100%;
        transition: width 0.3s ease;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .completed { background: #4CAF50; }
    .current { background: #FF9800; }
    .locked { background: #ccc; }
</style>
""", unsafe_allow_html=True)

# Available skills
SKILLS = ["Prompt Engineering"]

# Initialize session state
defaults = {
    "chat_history": [],
    "user_info": {},
    "skills": SKILLS,
    "selected_skill": None,
    "skill_level": None,
    "learning_path": [],
    "current_unit": 0,
    "stage": "welcome",
    "ai_error": "",
    "messages_count": 0,
    "max_free_messages": 50
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def huggingface_chat(messages, temperature=0.7, max_tokens=512):
    """Chat function using HuggingFace GPT-Neo-2.7B model"""
    API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
    
    # Get API key from secrets
    API_KEY = st.secrets.get("HUGGINGFACE_API_KEY", "")
    if not API_KEY:
        return None, "HuggingFace API key not found. Please add it to your secrets."
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Format conversation for the model
    conversation = ""
    for msg in messages:
        if msg["role"] == "system":
            conversation += f"System: {msg['content']}\n"
        elif msg["role"] == "user":
            conversation += f"Human: {msg['content']}\n"
        elif msg["role"] == "assistant":
            conversation += f"Assistant: {msg['content']}\n"
    
    conversation += "Assistant:"
    
    payload = {
        "inputs": conversation,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 503:
            return None, "Model is loading. Please wait a moment and try again."
        
        if response.status_code != 200:
            return None, f"API Error: Status {response.status_code}: {response.text[:200]}"
            
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "").strip()
            # Clean up the response
            generated_text = generated_text.split("Human:")[0].strip()
            return generated_text, ""
        else:
            return None, "Invalid response format from API"
            
    except Exception as e:
        return None, f"Connection Error: {str(e)}"

def show_header():
    """Display the main header"""
    st.markdown('<h1 class="main-header">🎓 Skilvyn</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Personalized AI Learning Companion</p>', unsafe_allow_html=True)

def show_learning_path():
    """Display the learning path progress"""
    if st.session_state.learning_path and st.session_state.stage in ["in_unit", "path_complete"]:
        progress = (st.session_state.current_unit / len(st.session_state.learning_path)) * 100
        
        st.markdown(f"""
        <div class="learning-path">
            <h3>📚 Your Learning Journey - {st.session_state.selected_skill}</h3>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <p>Progress: {st.session_state.current_unit}/{len(st.session_state.learning_path)} units completed</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show units
        for i, unit in enumerate(st.session_state.learning_path):
            if i < st.session_state.current_unit:
                status = "completed"
                icon = "✅"
            elif i == st.session_state.current_unit:
                status = "current"
                icon = "🔥"
            else:
                status = "locked"
                icon = "🔒"
            
            st.markdown(f"""
            <div class="unit-card">
                <span class="status-indicator {status}"></span>
                {icon} <strong>Unit {i+1}:</strong> {unit['title']}
                <br><small>{unit['objective']}</small>
            </div>
            """, unsafe_allow_html=True)

def show_chat():
    """Display chat messages"""
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f'<div class="assistant-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)

def check_message_limit():
    """Check if user has exceeded free message limit"""
    if st.session_state.messages_count >= st.session_state.max_free_messages:
        st.warning(f"You've reached the free message limit ({st.session_state.max_free_messages} messages). Upgrade to continue learning!")
        return False
    return True

def generate_ai_response(system_content, user_input=None):
    """Generate AI response with error handling"""
    if not check_message_limit():
        return None, "Message limit reached"
    
    messages = st.session_state.chat_history.copy()
    if user_input:
        messages.append({"role": "user", "content": user_input})
    
    system_msg = {"role": "system", "content": system_content}
    messages.append(system_msg)
    
    response, error = huggingface_chat(messages)
    
    if response:
        st.session_state.messages_count += 1
        
    return response, error

# Main interface
show_header()

# Show learning path if available
show_learning_path()

# Chat container
with st.container():
    show_chat()

# Message limit indicator
if st.session_state.messages_count > 0:
    remaining = st.session_state.max_free_messages - st.session_state.messages_count
    st.caption(f"Free messages remaining: {remaining}")

# Input placeholders based on stage
input_placeholders = {
    "welcome": "Enter your name or what you'd like me to call you...",
    "ask_info": "Enter your email address...",
    "choose_skill": "Enter your birth date (example: 1990-01-01)...",
    "ask_level": "Do you want to learn prompt engineering? (yes/no)...",
    "generate_path": "Describe your current experience in this field...",
    "in_unit": "Ask or answer through chat...",
    "path_complete": ""
}

user_input = st.chat_input(input_placeholders.get(st.session_state.stage, "Write your message here..."))

# Handle user input based on current stage
if user_input and st.session_state.stage != "path_complete":
    
    # Welcome stage
    if st.session_state.stage == "welcome":
        if not st.session_state.chat_history:
            # Initial welcome message
            welcome_content = """You are a friendly and warm AI learning assistant for the 'Skilvyn' platform. 
            Welcome the user warmly, introduce Skilvyn as an interactive learning platform powered by AI. 
            Ask them what name they'd like to be called. Be friendly and encouraging."""
            
            response, error = generate_ai_response(welcome_content)
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            elif error:
                st.session_state.ai_error = error
        
        if user_input:
            st.session_state.user_info["name"] = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            ask_email_content = f"""The user said their name is '{user_input}'. 
            Thank them warmly and ask for their email address. Use their name in the conversation."""
            
            response, error = generate_ai_response(ask_email_content)
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.session_state.stage = "ask_info"
            elif error:
                st.session_state.ai_error = error
            st.rerun()
    
    # Ask for email
    elif st.session_state.stage == "ask_info":
        st.session_state.user_info["email"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        ask_birth_content = "Ask the user warmly for their birth date in the format (YYYY-MM-DD)."
        
        response, error = generate_ai_response(ask_birth_content)
        if response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.stage = "choose_skill"
        elif error:
            st.session_state.ai_error = error
        st.rerun()
    
    # Ask for date of birth
    elif st.session_state.stage == "choose_skill":
        st.session_state.user_info["birth"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        skill_content = """Tell the user that 'Prompt Engineering' is the only skill available currently, 
        and that other skills will be added soon. Ask them if they want to start learning prompt engineering."""
        
        response, error = generate_ai_response(skill_content)
        if response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.stage = "ask_level"
        elif error:
            st.session_state.ai_error = error
        st.rerun()
    
    # Confirm skill selection
    elif st.session_state.stage == "ask_level":
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        if any(word in user_input.lower() for word in ["yes", "sure", "okay", "want", "would like"]):
            st.session_state.selected_skill = "Prompt Engineering"
            
            level_content = """Ask the user to describe their current experience level in prompt engineering 
            (beginner/intermediate/advanced or a short sentence about themselves)."""
            
            response, error = generate_ai_response(level_content)
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.session_state.stage = "generate_path"
            elif error:
                st.session_state.ai_error = error
        else:
            sorry_content = "Thank the user and tell them that other skills will be added soon."
            response, error = generate_ai_response(sorry_content)
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.session_state.stage = "welcome"
            elif error:
                st.session_state.ai_error = error
        st.rerun()
    
    # Generate learning path
    elif st.session_state.stage == "generate_path":
        st.session_state.skill_level = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Create a predefined learning path since JSON generation might be complex
        learning_path = [
            {
                "title": "Introduction to Prompt Engineering",
                "objective": "Understanding the fundamentals of prompt engineering and its importance",
                "welcome": "Welcome to your prompt engineering learning journey! We'll start with the basics."
            },
            {
                "title": "Writing Effective Prompts",
                "objective": "Learn techniques for writing clear and specific prompts",
                "welcome": "Now we'll learn how to write prompts that get the results you want."
            },
            {
                "title": "Using Context in Prompts",
                "objective": "Master the use of context to improve response quality",
                "welcome": "We'll dive deep into how to use context to make your prompts more accurate."
            },
            {
                "title": "Advanced Prompt Engineering Techniques",
                "objective": "Learn advanced techniques like Chain of Thought",
                "welcome": "Time to learn the advanced techniques that experts use."
            },
            {
                "title": "Practical Applications and Projects",
                "objective": "Apply what you've learned to real-world projects",
                "welcome": "We'll conclude by applying everything you've learned to practical projects."
            }
        ]
        
        st.session_state.learning_path = learning_path
        st.session_state.current_unit = 0
        st.session_state.stage = "in_unit"
        
        unit = learning_path[0]
        unit_content = f"""Welcome the user to the first unit: {unit['title']}. 
        {unit['welcome']} Invite them to start learning and chatting."""
        
        response, error = generate_ai_response(unit_content)
        if response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        elif error:
            st.session_state.ai_error = error
        st.rerun()
    
    # In unit learning
    elif st.session_state.stage == "in_unit":
        unit = st.session_state.learning_path[st.session_state.current_unit]
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        tutor_content = f"""You are a specialized AI tutor. This is the unit: {unit['title']}. 
        Objective: {unit['objective']}. Answer the user's question or continue the lesson interactively. 
        At the end of your response, on a new line, write [status:pass] if the user is ready for the next unit, 
        or [status:stay] if they should remain in this unit."""
        
        response, error = generate_ai_response(tutor_content, user_input)
        if response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Check for progression
            if "[status:pass]" in response:
                if st.session_state.current_unit + 1 < len(st.session_state.learning_path):
                    st.session_state.current_unit += 1
                    next_unit = st.session_state.learning_path[st.session_state.current_unit]
                    
                    next_content = f"""Congratulate the user for completing the previous unit and welcome them to the next unit: 
                    {next_unit['title']}. {next_unit['welcome']}"""
                    
                    next_response, next_error = generate_ai_response(next_content)
                    if next_response:
                        st.session_state.chat_history.append({"role": "assistant", "content": next_response})
                else:
                    st.session_state.stage = "path_complete"
                    complete_content = "Congratulate the user for successfully completing all units."
                    complete_response, complete_error = generate_ai_response(complete_content)
                    if complete_response:
                        st.session_state.chat_history.append({"role": "assistant", "content": complete_response})
        elif error:
            st.session_state.ai_error = error
        st.rerun()

# Path complete stage
elif st.session_state.stage == "path_complete":
    st.success("🎉 Congratulations! You've successfully completed the program!")
    if st.button("🔄 Start Again"):
        for k in ["chat_history", "user_info", "selected_skill", "skill_level", 
                  "learning_path", "current_unit", "stage", "ai_error", "messages_count"]:
            st.session_state[k] = defaults[k]
        st.rerun()

# Display errors if any
if st.session_state.get("ai_error"):
    st.error(st.session_state.ai_error)
    if st.button("Try Again"):
        st.session_state.ai_error = ""
        st.rerun()

# Sidebar with user info
if st.session_state.user_info:
    with st.sidebar:
        st.header("👤 User Information")
        if "name" in st.session_state.user_info:
            st.write(f"**Name:** {st.session_state.user_info['name']}")
        if "email" in st.session_state.user_info:
            st.write(f"**Email:** {st.session_state.user_info['email']}")
        if st.session_state.selected_skill:
            st.write(f"**Selected Skill:** {st.session_state.selected_skill}")
        
        st.write(f"**Messages Used:** {st.session_state.messages_count}/{st.session_state.max_free_messages}")
