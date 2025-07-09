import streamlit as st
import openai

# Page setup must be at the very top
st.set_page_config(page_title="Skilvyn", layout="wide")

# Load OpenAI API key with error handling
if "OPENAI_API_KEY" not in st.secrets:
    st.error("OPENAI_API_KEY is not set in Streamlit secrets.")
    st.stop()
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 0. Initialize session_state defaults
for key in ("user_info_complete", "plan_generated"):
    if key not in st.session_state:
        st.session_state[key] = False

# Utility: generate dynamic UI labels with AI
@st.cache_data(show_spinner=False)
def ai_label(task_description: str) -> str:
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a concise, friendly UI prompt writer."},
                {"role": "user",   "content": f"Generate one short label to {task_description}."}
            ],
            temperature=0.7,
            max_tokens=32
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return task_description.capitalize()

# 1. Onboarding: collect immutable user info
if not st.session_state["user_info_complete"]:
    st.title(ai_label("welcome the user to Skilvyn"))
    st.info(ai_label("introduce the onboarding process"))
    name  = st.text_input(ai_label("ask the user for their name"))
    email = st.text_input(ai_label("ask the user for their email address"))
    birth = st.date_input(ai_label("ask the user for their date of birth"))
    # Simple email validation
    valid_email = "@" in email if email else False
    if st.button(ai_label("offer a save and continue button")) and name and valid_email and birth:
        st.session_state.update({
            "name": name,
            "email": email,
            "birth": str(birth),
            "user_info_complete": True
        })
        st.experimental_rerun()
    elif email and not valid_email:
        st.warning("Please enter a valid email address.")
    st.stop()

# 2. Onboarding: select skill & generate 7-day plan
if not st.session_state["plan_generated"]:
    greeting = ai_label(f"greet the user by name {st.session_state['name']}")
    st.title(greeting)
    st.info(ai_label("announce that Prompt Engineering is the first skill"))
    skill   = "Prompt Engineering"
    level   = st.selectbox(ai_label("ask the user to rate their current skill level"),
                           ["Beginner", "Intermediate", "Advanced"])
    minutes = st.slider(ai_label("ask how many minutes per day they can study"),
                        10, 120, 30)
    goal    = st.text_input(ai_label("ask the user to state their learning goal in one sentence"))
    if st.button(ai_label("offer to generate the 7-day roadmap")) and goal:
        system_prompt = ai_label("define the system role for a personalized AI learning coach")
        user_prompt = (
            f"Skill: {skill}\n"
            f"Student: {st.session_state['name']} ({st.session_state['email']})\n"
            f"Experience: {level}\n"
            f"Daily time: {minutes} minutes\n"
            f"Goal: {goal}\n"
            "Generate a 7-day learning plan table with columns: Day, Topic, Exercise prompt, Estimated time, Tip."
        )
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature=0.7,
            )
            st.session_state.update({
                "daily_plan": resp.choices[0].message.content,
                "plan_generated": True,
                "current_skill": skill
            })
            st.experimental_rerun()
        except Exception:
            st.error("Failed to generate learning plan. Please try again.")
    st.stop()

# 3. Main interface: show learning plan & AI-tutor chat
st.markdown("## Your 7-Day Learning Plan")
st.sidebar.markdown(st.session_state["daily_plan"])

st.header(f"Skilvyn — {st.session_state['current_skill']}")
st.subheader(ai_label("label the AI chat tutor section"))

# 4. Chat input & response
user_input = st.text_input(ai_label("prompt the user to ask a question or request help"))
if st.button(ai_label("send the user's question to the tutor")) and user_input:
    with st.spinner("Generating…"):
        try:
            tutor_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",  "content": "You are a helpful AI tutor."},
                    {"role": "user",    "content": user_input}
                ],
                temperature=0.7,
            )
            st.success("Here’s your answer:")
            st.write(tutor_resp.choices[0].message.content)
        except Exception:
            st.error("Failed to get a response from the AI tutor. Please try again.")
```0
