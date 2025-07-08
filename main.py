import streamlit as st import openai

Load API key

openai.api_key = st.secrets["OPENAI_API_KEY"]

--- Onboarding Wizard: personalize a 7-day plan ---

def generate_learning_path(name, level, minutes, goal): system_prompt = "You are an AI learning coach." user_prompt = ( f"Student: {name}\n" f"Level: {level}\n" f"Daily time: {minutes} minutes\n" f"Goal: {goal}\n" "Generate a 7-day learning plan as a Markdown table: Day, Topic, Exercise prompt, Estimated time, Tip." ) resp = openai.ChatCompletion.create( model="gpt-3.5-turbo", messages=[ {"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt} ], temperature=0.7 ) return resp.choices[0].message.content

if "setup_done" not in st.session_state: st.title("Welcome to Skilvyn") st.text("Let's personalize your 7-day AI learning plan.") name = st.text_input("Your name") level = st.selectbox("Your AI skill level", ["Beginner", "Intermediate", "Advanced"]) minutes = st.slider("Minutes per day", 10, 120, 30) goal = st.text_input("Your learning goal") if st.button("Create my 7-day plan") and name and goal: st.session_state["daily_plan"] = generate_learning_path(name, level, minutes, goal) st.session_state["setup_done"] = True st.experimental_rerun() st.stop()

--- After onboarding: display plan and modules ---

st.sidebar.header("My 7-Day Plan") st.sidebar.markdown(st.session_state["daily_plan"])

Page configuration

st.set_page_config(page_title="Skilvyn", layout="wide") st.title("Skilvyn – Your AI Skills Classroom")

Modules selector

modules = [ "Basics of Prompt Engineering", "Chain-of-Thought Prompts", "Few-Shot Prompting", ] selected = st.sidebar.selectbox("Choose a module", modules)

Tabs for Lesson, Exercise, Examples

tabs = st.tabs(["Lesson", "Exercise", "Examples"])

with tabs[0]: st.header(f"Module: {selected}") if selected == "Basics of Prompt Engineering": st.markdown( """ What is a prompt?
A prompt is the instruction you give to AI to guide its output.
- Start with a clear role: “You are an AI instructor…”
- Specify the task clearly: “Explain chain-of-thought prompting…” """ ) elif selected == "Chain-of-Thought Prompts": st.markdown( """ Chain-of-Thought
A technique where the AI is guided step-by-step, e.g.:
1. Define the problem
2. Break it into sub-steps
3. Ask for reasoning before answering """ ) else: st.markdown( """ Few-Shot Prompting
Provide examples in the prompt to guide output:
```
Q: Translate English to French. A: Hello →

