import streamlit as st
import openai

openai.api_key = "<YOUR_OPENAI_KEY>"

st.set_page_config(page_title="SkillForge AI", layout="centered")
st.title("SkillForge AI – Learn AI Skills")
st.write("Enter a product name or URL to generate a cart recovery email.")

product = st.text_input("Product name or URL")
if st.button("Generate Email"):
    if not product:
        st.error("Please enter a product name or URL.")
    else:
        prompt = f"""
You are an expert in crafting cart recovery emails. The customer abandoned {product} in the cart.
Write:
1. A compelling subject line.
2. The email body with features, incentive, and clear CTA.
3. Add a P.S. to reduce risk.
"""
        with st.spinner("Generating…"):
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":prompt}],
                temperature=0.7,
                max_tokens=300
            )
        email = resp.choices[0].message.content.strip()
        st.text_area("Generated Email:", value=email, height=200)
