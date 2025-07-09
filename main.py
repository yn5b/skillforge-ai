import streamlit as st
import requests

st.set_page_config(page_title="Skilvyn Tutor", layout="wide")

SKILLS = ["Prompt Engineering"]

defaults = {
    "chat_history": [],
    "user_info": {},
    "skills": SKILLS,
    "selected_skill": None,
    "skill_level": None,
    "learning_path": [],
    "current_unit": 0,
    "unit_passed": False,
    "stage": "welcome"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def flan_t5_chat(messages, temperature=0.7, max_tokens=256):
    HF_TOKEN = st.secrets.get("HF_API_KEY", "")
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"Instruction: {msg['content']}\n"
        elif msg["role"] == "user":
            prompt += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"Assistant: {msg['content']}\n"
    prompt += "Assistant:"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "do_sample": True
        }
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        # DEBUG: Show raw response for troubleshooting
        # st.write("DEBUG RESPONSE TEXT:", response.text)

        # If status code is not 200, show error
        if response.status_code != 200:
            return f"[Connection Error]: HuggingFace API returned status {response.status_code}: {response.text}"
        try:
            result = response.json()
        except Exception as e:
            return f"[Connection Error]: Could not decode JSON. Raw response: {response.text[:200]}"
        # Huggingface may return dict with error
        if isinstance(result, dict) and "error" in result:
            return f"[AI Error]: {result['error']}"
        elif isinstance(result, list) and 'generated_text' in result[0]:
            return result[0]['generated_text'].split("Assistant:")[-1].strip()
        elif isinstance(result, list) and 'generated_text' in result[0]:
            return result[0]['generated_text']
        else:
            return str(result)
    except Exception as e:
        return f"[Connection Error]: {e}"

def show_chat():
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.chat_message("assistant").markdown(msg["content"])
        else:
            st.chat_message("user").markdown(msg["content"])

show_chat()

input_placeholder = {
    "welcome": "Enter your name or how you'd like to be addressed...",
    "ask_info": "Enter your email address...",
    "choose_skill": "Enter your date of birth (e.g., 1990-01-01)...",
    "ask_level": "Would you like to learn Prompt Engineering? (yes/no)...",
    "generate_path": "Describe your current experience...",
    "in_unit": "Ask or answer via chat...",
    "path_complete": ""
}.get(st.session_state.stage, "")

user_input = st.chat_input(input_placeholder)

def fallback_welcome():
    return "👋 Welcome to Skilvyn! (AI service is temporarily unavailable, but you can still use the app.)\nWhat name should I call you?"

if st.session_state.stage == "welcome":
    if not st.session_state.chat_history:
        system_prompt = {
            "role": "system",
            "content": "You are a friendly AI learning assistant. Greet the user, introduce Skilvyn as an interactive AI-powered learning platform which generates everything via AI, and ask for the user's name or how they want to be addressed."
        }
        assistant_reply = flan_t5_chat([system_prompt])
        # Always show welcome message, even if failed
        if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
            assistant_reply = fallback_welcome() + "\n\n" + assistant_reply
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    if user_input:
        st.session_state.user_info["name"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": f"You are a friendly AI learning assistant. The user said their name is {user_input}. Politely ask them for their email address."
        }
        assistant_reply = flan_t5_chat(st.session_state.chat_history + [system_prompt])
        if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
            assistant_reply = "Can you give me your email address?" + "\n\n" + assistant_reply
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.stage = "ask_info"
        st.experimental_rerun()

elif st.session_state.stage == "ask_info":
    if user_input:
        st.session_state.user_info["email"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": "Politely ask the user for their date of birth (format: YYYY-MM-DD)."
        }
        assistant_reply = flan_t5_chat(st.session_state.chat_history + [system_prompt])
        if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
            assistant_reply = "Can you give me your date of birth? (YYYY-MM-DD)" + "\n\n" + assistant_reply
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.stage = "choose_skill"
        st.experimental_rerun()

elif st.session_state.stage == "choose_skill":
    if user_input:
        st.session_state.user_info["birth"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": "Tell the user that currently only 'Prompt Engineering' is available to learn, and more skills will be added soon. Ask them to confirm if they want to start learning Prompt Engineering."
        }
        assistant_reply = flan_t5_chat(st.session_state.chat_history + [system_prompt])
        if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
            assistant_reply = "Currently we only have Prompt Engineering. Do you want to start learning it? (yes/no)" + "\n\n" + assistant_reply
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.stage = "ask_level"
        st.experimental_rerun()

elif st.session_state.stage == "ask_level":
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        if user_input.strip().lower() == "yes":
            st.session_state.selected_skill = "Prompt Engineering"
            system_prompt = {
                "role": "system",
                "content": "Ask the user to briefly describe their current experience level in Prompt Engineering (beginner/intermediate/advanced or a short sentence about themselves)."
            }
            assistant_reply = flan_t5_chat(st.session_state.chat_history + [system_prompt])
            if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
                assistant_reply = "Please describe your experience with Prompt Engineering." + "\n\n" + assistant_reply
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.stage = "generate_path"
            st.experimental_rerun()
        else:
            sorry_prompt = {
                "role": "system",
                "content": "Thank the user and let them know more skills will be added soon."
            }
            assistant_reply = flan_t5_chat(st.session_state.chat_history + [sorry_prompt])
            if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
                assistant_reply = "Thank you for your interest! More skills will be added soon." + "\n\n" + assistant_reply
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.stage = "welcome"
            st.experimental_rerun()

elif st.session_state.stage == "generate_path":
    if user_input:
        st.session_state.skill_level = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        plan_prompt = {
            "role": "system",
            "content": (
                f"Create a personalized learning plan for {st.session_state.user_info['name']} who wants to learn Prompt Engineering. "
                f"Their experience: {st.session_state.skill_level}. "
                "The plan should have 5 units. For each unit, provide a short title, a learning objective, and a welcome message. Respond with valid JSON: [{\"title\":..., \"objective\":..., \"welcome\":...}, ...]"
            )
        }
        plan_json = flan_t5_chat(st.session_state.chat_history + [plan_prompt])
        import json
        try:
            learning_path = json.loads(plan_json)
            st.session_state.learning_path = learning_path
            st.session_state.current_unit = 0
            st.session_state.stage = "in_unit"
            unit = learning_path[0]
            unit_prompt = {
                "role": "system",
                "content": f"Welcome the user to the first unit: {unit['title']}. {unit['welcome']} Invite them to start learning and chatting."
            }
            assistant_reply = flan_t5_chat(st.session_state.chat_history + [unit_prompt])
            if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
                assistant_reply = f"Let's start! **{unit['title']}**: {unit['welcome']}" + "\n\n" + assistant_reply
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.experimental_rerun()
        except Exception:
            st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, something went wrong generating your learning path. Please try again."})
            st.session_state.stage = "welcome"
            st.experimental_rerun()

elif st.session_state.stage == "in_unit":
    unit = st.session_state.learning_path[st.session_state.current_unit]
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        tutor_prompt = {
            "role": "system",
            "content": (
                f"You are an AI tutor. This is unit: {unit['title']}. Objective: {unit['objective']}. "
                "Answer the user's question or continue the lesson conversationally. "
                "At the end, on a new line, write [status:pass] if the user is ready for the next unit, or [status:stay] if they should stay in this unit."
            )
        }
        assistant_reply = flan_t5_chat(st.session_state.chat_history + [tutor_prompt])
        if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
            assistant_reply = "Let's continue! (AI service is temporarily unavailable)" + "\n\n" + assistant_reply
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

        if "[status:pass]" in assistant_reply:
            if st.session_state.current_unit + 1 < len(st.session_state.learning_path):
                st.session_state.current_unit += 1
                next_unit = st.session_state.learning_path[st.session_state.current_unit]
                next_unit_prompt = {
                    "role": "system",
                    "content": f"Congratulate the user for completing the previous unit and welcome them to the next unit: {next_unit['title']}. {next_unit['welcome']}"
                }
                assistant_reply = flan_t5_chat(st.session_state.chat_history + [next_unit_prompt])
                if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
                    assistant_reply = f"Next unit: **{next_unit['title']}** {next_unit['welcome']}" + "\n\n" + assistant_reply
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                st.experimental_rerun()
            else:
                st.session_state.stage = "path_complete"
                complete_prompt = {
                    "role": "system",
                    "content": "Congratulate the user for completing all units."
                }
                assistant_reply = flan_t5_chat(st.session_state.chat_history + [complete_prompt])
                if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
                    assistant_reply = "🎉 Congratulations! You have completed the course." + "\n\n" + assistant_reply
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                st.experimental_rerun()
        elif "[status:stay]" in assistant_reply:
            encourage_prompt = {
                "role": "system",
                "content": "Encourage the user to keep working on this unit until they're ready to move on."
            }
            assistant_reply = flan_t5_chat(st.session_state.chat_history + [encourage_prompt])
            if assistant_reply.startswith("[AI Error]") or assistant_reply.startswith("[Connection Error]"):
                assistant_reply = "Keep working on this unit! (AI service is temporarily unavailable)" + "\n\n" + assistant_reply
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.experimental_rerun()

elif st.session_state.stage == "path_complete":
    st.success("You have completed the program! You can start over or review your units.")
    if st.button("Start Over"):
        for k in ("chat_history", "user_info", "selected_skill", "skill_level", "learning_path", "current_unit", "stage"):
            st.session_state[k] = defaults[k]
        st.experimental_rerun()
