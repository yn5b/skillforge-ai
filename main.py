"""
SkillForge AI – Streamlit app for learning skills with AI.
Usage:
    pip install -r requirements.txt
    streamlit run main.py
"""
import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="SkillForge AI")
st.title("SkillForge AI – Learn Skills with AI")
st.write("Enter input and generate AI-powered output.")

user_input = st.text_input("Your input")
if st.button("Generate"):
    if not user_input:
        st.error("Please enter some input.")
    else:
        prompt = f"Generate helpful response for: {user_input}"
        with st.spinner("Generating…"):
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":prompt}],
                temperature=0.7,
                max_tokens=300
            )
            output = resp.choices[0].message.content.strip()
        st.text_area("Generated Output:", value=output, height=200)
