import streamlit as st
import openai
import time
import openai.error  # ← هنا استورد الاستثناءات

# Load your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 1. عرّف الدالة بعد الاستيرادات
def generate_learning_path(name, level, minutes, goal):
    system_prompt = "You are a learning coach AI."
    user_prompt = (
        f"Generate a 7-day learning plan table for {name}, "
        f"{level}, {minutes} min/day, goal: {goal}."
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
        return resp.choices[0].message.content
    except openai.error.RateLimitError:
        # عند تجاوز الحد، انتظر ثم أعد المحاولة
        time.sleep(5)
        return None

# 2. شاشة الـ Onboarding Wizard
if "setup_done" not in st.session_state:
    st.title("Welcome to Skilvyn")
    name    = st.text_input("Your name")
    level   = st.selectbox("Your AI skill level", ["Beginner","Intermediate","Advanced"])
    minutes = st.slider("Minutes per day", 10, 120, 30)
    goal    = st.text_input("Your learning goal")

    if st.button("Create my 7-day plan") and name and goal:
        plan = generate_learning_path(name, level, minutes, goal)
        if plan is None:
            st.error("⚠️ Hit the OpenAI rate limit. Please wait a moment and try again.")
        else:
            st.session_state["daily_plan"] = plan
            st.session_state["setup_done"]  = True
            st.experimental_rerun()
    st.stop()

# 3. بعد الإعداد: عرض الخطة في الشريط الجانبي
st.sidebar.header("My 7-Day Plan")
st.sidebar.markdown(st.session_state["daily_plan"])

# 4. إعداد الصفحة والـ Modules
st.set_page_config(page_title="SkillForge AI", layout="wide")
st.title("Skilvyn – Your AI Skills Classroom")

modules = [
    "Basics of Prompt Engineering",
    "Chain-of-Thought Prompts",
    "Few-Shot Prompting",
]
selected_module = st.sidebar.selectbox("Choose a module", modules)

# 5. إنشاء تبويبات لكل وحدة: درس، تمرين، أمثلة
tabs = st.tabs(["Lesson", "Exercise", "Examples"])

with tabs[0]:
    if selected_module == "Basics of Prompt Engineering":
        st.header("Module 1: Basics of Prompt Engineering")
        st.markdown("""
        **What is a prompt?**  
        A prompt is the instruction you give to the AI to guide its output.  
        - Start with a **clear role**: “You are an AI instructor…”  
        - Specify the **task**: “Explain what chain-of-thought prompting is…”
        """)

with tabs[1]:
    st.header(f"Exercise: {selected_module}")
    user_input = st.text_area("Enter your prompt here")
    if st.button("Run Exercise"):
        if user_input:
            system_message = "You are a friendly AI prompt engineering instructor."
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
            )
            st.subheader("AI Response")
            st.write(resp.choices[0].message.content)
        else:
            st.error("Please enter a prompt to run the exercise.")

with tabs[2]:
    st.header("Example Prompts & Outputs")
    if selected_module == "Basics of Prompt Engineering":
        st.markdown("""
        **Example Prompt**:  
        ``` 
        You are an AI instructor. Explain what a 'prompt' is and give three tips for writing clear prompts.
        ```
        **Example Output**:  
        1. A prompt is…  
        2. Tip 1: Be specific…  
        3. Tip 2: Provide context…  
        4. Tip 3: Specify the desired format…
        """)
```0
