import streamlit as st
import ollama

# Initialize session state for managing user data and app state
defaults = {
    "chat_history": [],  # Stores conversation history
    "user_info": {},     # Stores user personal information
    "skills": ["Prompt Engineering"],  # Available skills
    "selected_skill": None,  # Currently selected skill
    "skill_level": None,    # User's experience level
    "learning_path": [],    # Learning path units
    "current_unit": 0,      # Current unit index
    "stage": "welcome",     # Current stage of the app
    "ai_error": "",         # Stores API errors
    "messages_count": 0,    # Tracks number of AI messages
    "max_free_messages": 50,  # Free message limit
    "max_history_size": 20    # Max chat history size
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Function to generate AI response using local Ollama model
def generate_ai_response(system_content, user_input=None):
    if not check_message_limit():
        return None, "Message limit reached"

    # Prepare messages for Ollama
    messages = st.session_state.chat_history.copy()
    if user_input:
        messages.append({"role": "user", "content": user_input})

    # Add system content if available
    if system_content:
        messages.insert(0, {"role": "system", "content": system_content})

    try:
        # Call Ollama chat with the local model
        response = ollama.chat(model="tinyllama_local", messages=messages)
        return response['message']['content'], ""
    except Exception as e:
        return None, f"Ollama Error: {str(e)}"

# Function to check message limit
def check_message_limit():
    if st.session_state.messages_count >= st.session_state.max_free_messages:
        st.warning(f"You've reached the free message limit ({st.session_state.max_free_messages} messages). Upgrade to continue learning!")
        return False
    return True

# Function to trim chat history
def trim_chat_history():
    if len(st.session_state.chat_history) > st.session_state.max_history_size:
        st.session_state.chat_history = st.session_state.chat_history[-st.session_state.max_history_size:]

# Main app logic
def main():
    # Page configuration
    st.set_page_config(
        page_title="Skilvyn - AI Learning Tutor",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Show header
    st.markdown('<h1 class="main-header">🎓 Skilvyn</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Personalized AI Learning Companion</p>', unsafe_allow_html=True)

    # Show learning path if available
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

    # Chat container
    with st.container():
        # Show chat messages
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="assistant-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
            elif msg["role"] == "user":
                st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)

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
                Thank them warmly and ask for their email address."""

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

            # For simplicity, use a predefined learning path
            learning_path = [
                {
                    "title": "Introduction to Prompt Engineering",
                    "objective": "Understanding the fundamentals of prompt engineering and its importance",
                    "welcome": "Welcome to your prompt engineering learning journey! We'll start with the basics."
                },
                # ... (other units)
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

            response, error = generate_ai_response(tutor_content)
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})

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

        # Performance info
        st.subheader("📊 Performance")
        st.write(f"**History Size:** {len(st.session_state.chat_history)}/{st.session_state.max_history_size}")

        # Clear history button for testing
        if st.button("🧹 Clear Old History"):
            trim_chat_history()
            st.success("History trimmed!")
