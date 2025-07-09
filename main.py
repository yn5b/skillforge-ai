import streamlit as st
import requests  # Only needed if you have an external Llama 2 API endpoint

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

# --------- Llama 2 7B API Wrapper ---------
def llama2_chat(messages, temperature=0.7, max_tokens=256):
    """
    This function should call your actual Llama 2 7B model.
    Below is a placeholder for an API call.
    Modify this according to your real server or model invocation.
    Always pass the full list of messages (context) for a smart, interactive AI experience.
    """
    # Example: If you have a local or external endpoint:
    # response = requests.post(
    #     "http://localhost:8000/v1/chat/completions",
    #     json={"messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    # )
    # return response.json()["choices"][0]["message"]["content"]

    # If you don't have a ready server, you can try the HuggingFace inference API or any available service.
    # For now, just return a placeholder message for the user:
    return "[!] The AI backend is not yet connected. Please connect Llama 2 API for real responses."

def show_chat():
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.chat_message("assistant").markdown(msg["content"])
        else:
            st.chat_message("user").markdown(msg["content"])

# ---------- App Flow Logic ----------

show_chat()

# Set the input placeholder according to the current stage
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

# Welcome stage: ask for name
if st.session_state.stage == "welcome":
    if not st.session_state.chat_history:
        system_prompt = {
            "role": "system",
            "content": "You are a friendly AI learning assistant. Greet the user, introduce Skilvyn as an interactive AI-powered learning platform which generates everything via AI, and ask for the user's name or how they want to be addressed."
        }
        assistant_reply = llama2_chat([system_prompt])
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    if user_input:
        st.session_state.user_info["name"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": f"You are a friendly AI learning assistant. The user said their name is {user_input}. Politely ask them for their email address."
        }
        assistant_reply = llama2_chat(st.session_state.chat_history + [system_prompt])
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.stage = "ask_info"
        st.experimental_rerun()

# Email stage
elif st.session_state.stage == "ask_info":
    if user_input:
        st.session_state.user_info["email"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": "Politely ask the user for their date of birth (format: YYYY-MM-DD)."
        }
        assistant_reply = llama2_chat(st.session_state.chat_history + [system_prompt])
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.stage = "choose_skill"
        st.experimental_rerun()

# Birth date stage
elif st.session_state.stage == "choose_skill":
    if user_input:
        st.session_state.user_info["birth"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": "Tell the user that currently only 'Prompt Engineering' is available to learn, and more skills will be added soon. Ask them to confirm if they want to start learning Prompt Engineering."
        }
        assistant_reply = llama2_chat(st.session_state.chat_history + [system_prompt])
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.stage = "ask_level"
        st.experimental_rerun()

# Skill confirmation stage
elif st.session_state.stage == "ask_level":
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        if user_input.strip().lower() == "yes":
            st.session_state.selected_skill = "Prompt Engineering"
            system_prompt = {
                "role": "system",
                "content": "Ask the user to briefly describe their current experience level in Prompt Engineering (beginner/intermediate/advanced or a short sentence about themselves)."
            }
            assistant_reply = llama2_chat(st.session_state.chat_history + [system_prompt])
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.stage = "generate_path"
            st.experimental_rerun()
        else:
            sorry_prompt = {
                "role": "system",
                "content": "Thank the user and let them know more skills will be added soon."
            }
            assistant_reply = llama2_chat(st.session_state.chat_history + [sorry_prompt])
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.stage = "welcome"
            st.experimental_rerun()

# Generate learning path stage
elif st.session_state.stage == "generate_path":
    if user_input:
        st.session_state.skill_level = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        # Ask the AI to generate a learning plan
        plan_prompt = {
            "role": "system",
            "content": (
                f"Create a personalized learning plan for {st.session_state.user_info['name']} who wants to learn Prompt Engineering. "
                f"Their experience: {st.session_state.skill_level}. "
                "The plan should have 5 units. For each unit, provide a short title, a learning objective, and a welcome message. Respond with valid JSON: [{\"title\":..., \"objective\":..., \"welcome\":...}, ...]"
            )
        }
        plan_json = llama2_chat(st.session_state.chat_history + [plan_prompt])
        import json
        try:
            learning_path = json.loads(plan_json)
            st.session_state.learning_path = learning_path
            st.session_state.current_unit = 0
            st.session_state.stage = "in_unit"
            # Welcome message for the first unit
            unit = learning_path[0]
            unit_prompt = {
                "role": "system",
                "content": f"Welcome the user to the first unit: {unit['title']}. {unit['welcome']} Invite them to start learning and chatting."
            }
            assistant_reply = llama2_chat(st.session_state.chat_history + [unit_prompt])
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.experimental_rerun()
        except Exception:
            st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, something went wrong generating your learning path. Please try again."})
            st.session_state.stage = "welcome"
            st.experimental_rerun()

# Chat with AI in the unit
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
        assistant_reply = llama2_chat(st.session_state.chat_history + [tutor_prompt])
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

        if "[status:pass]" in assistant_reply:
            if st.session_state.current_unit + 1 < len(st.session_state.learning_path):
                st.session_state.current_unit += 1
                next_unit = st.session_state.learning_path[st.session_state.current_unit]
                next_unit_prompt = {
                    "role": "system",
                    "content": f"Congratulate the user for completing the previous unit and welcome them to the next unit: {next_unit['title']}. {next_unit['welcome']}"
                }
                assistant_reply = llama2_chat(st.session_state.chat_history + [next_unit_prompt])
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                st.experimental_rerun()
            else:
                st.session_state.stage = "path_complete"
                complete_prompt = {
                    "role": "system",
                    "content": "Congratulate the user for completing all units."
                }
                assistant_reply = llama2_chat(st.session_state.chat_history + [complete_prompt])
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                st.experimental_rerun()
        elif "[status:stay]" in assistant_reply:
            encourage_prompt = {
                "role": "system",
                "content": "Encourage the user to keep working on this unit until they're ready to move on."
            }
            assistant_reply = llama2_chat(st.session_state.chat_history + [encourage_prompt])
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.experimental_rerun()

# Path complete
elif st.session_state.stage == "path_complete":
    st.success("You have completed the program! You can start over or review your units.")
    if st.button("Start Over"):
        for k in ("chat_history", "user_info", "selected_skill", "skill_level", "learning_path", "current_unit", "stage"):
            st.session_state[k] = defaults[k]
        st.experimental_rerun()
