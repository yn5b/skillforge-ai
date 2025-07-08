import streamlit as st
import openai

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 1. Onboarding Wizard – gather user information
if "setup_done" not in st.session_state:
    st.title("Welcome to Skilvyn")
    user_name = st.text_input("Your name")
    user_level = st.selectbox(
        "Your AI skill level", ["Beginner", "Intermediate", "Advanced"]
    )
    daily_time = st.slider(
        "How many minutes per day can you dedicate?", 10, 120, 30
    )
    learning_goal = st.text_input("What is your learning goal?")
    
    if st.button("Generate My 7-Day Plan") and user_name and learning_goal:
        # Prepare prompts for GPT
        system_message = "You are an AI learning coach."
        user_message = (
            f"Generate a personalized 7-day learning plan table for "
            f"{user_name}, who is {user_level}, can spend {daily_time} minutes per day, "
            f"and has the goal: {learning_goal}."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )
        # Store the generated plan and mark setup as done
        st.session_state["daily_plan"] = response.choices[0].message.content
        st.session_state["setup_done"] = True
        st.experimental_rerun()
    
    # Stop execution here until onboarding is complete
    st.stop()

# 2. Display the generated 7-day plan in the sidebar
st.sidebar.header("My 7-Day Learning Plan")
st.sidebar.markdown(st.session_state["daily_plan"])

# 3. Main AI Tutor chat interface
st.header("AI Tutor Chat")
user_query = st.text_input("Enter your question or prompt")
if st.button("Send"):
    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI tutor."},
            {"role": "user", "content": user_query},
        ],
        temperature=0.7,
    )
    st.subheader("Response")
    st.write(chat_response.choices[0].message.content)
