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
    "stage": "welcome",
    "ai_error": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def falcon_chat(messages, temperature=0.7, max_tokens=256):
    HF_TOKEN = st.secrets.get("HF_API_KEY", "")
    API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    # Falcon تفهم التعليمات بشكل جيد على هيئة محادثة بشرية
    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"[System] {msg['content']}\n"
        elif msg["role"] == "user":
            prompt += f"[User] {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"[Assistant] {msg['content']}\n"
    prompt += "[Assistant]"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "do_sample": True
        }
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return None, f"[Connection Error]: Status {response.status_code}: {response.text[:200]}"
        try:
            result = response.json()
        except Exception:
            return None, f"[Connection Error]: Could not decode JSON. Raw response: {response.text[:200]}"
        if isinstance(result, dict) and "error" in result:
            return None, f"[AI Error]: {result['error']}"
        if isinstance(result, list) and 'generated_text' in result[0]:
            # Falcon sometimes returns the entire conversation after '[Assistant]'
            return result[0]['generated_text'].split("[Assistant]")[-1].strip(), ""
        return str(result), ""
    except Exception as e:
        return None, f"[Connection Error]: {e}"

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

# Always clear ai_error when there is user input
if user_input and st.session_state["ai_error"]:
    st.session_state["ai_error"] = ""

if st.session_state.stage == "welcome":
    if not st.session_state.chat_history:
        system_prompt = {
            "role": "system",
            "content": (
                "You are a friendly AI educational assistant for the platform 'Skilvyn'. "
                "Greet the user with an engaging and warm welcome message, introducing Skilvyn as an interactive AI-powered learning platform where all content is AI-generated. "
                "Ask the user what name they would like you to use for them. "
                "Base your greeting on the latest conversation context."
            )
        }
        assistant_reply, error = falcon_chat([system_prompt])
        if error or assistant_reply is None or not assistant_reply.strip():
            st.session_state["ai_error"] = error or "AI did not return a welcome message. Please check your API key or try again later."
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

    if st.session_state["ai_error"]:
        st.error(st.session_state["ai_error"])
    elif user_input:
        st.session_state.user_info["name"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": (
                f"You are a friendly AI assistant. The user said their name is '{user_input}'. "
                "Politely ask for their email address. Address the user by their chosen name if possible."
            )
        }
        assistant_reply, error = falcon_chat(st.session_state.chat_history + [system_prompt])
        if error or assistant_reply is None or not assistant_reply.strip():
            st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.stage = "ask_info"
        st.experimental_rerun()

elif st.session_state.stage == "ask_info":
    if user_input:
        st.session_state.user_info["email"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": (
                "Politely ask the user for their date of birth (format: YYYY-MM-DD)."
            )
        }
        assistant_reply, error = falcon_chat(st.session_state.chat_history + [system_prompt])
        if error or assistant_reply is None or not assistant_reply.strip():
            st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.session_state.stage = "choose_skill"
        st.experimental_rerun()

elif st.session_state.stage == "choose_skill":
    if user_input:
        st.session_state.user_info["birth"] = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        system_prompt = {
            "role": "system",
            "content": (
                "Inform the user that currently only 'Prompt Engineering' is available to learn, and more skills will be added soon. "
                "Ask them to confirm if they want to start learning Prompt Engineering."
            )
        }
        assistant_reply, error = falcon_chat(st.session_state.chat_history + [system_prompt])
        if error or assistant_reply is None or not assistant_reply.strip():
            st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
        else:
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
                "content": (
                    "Ask the user to briefly describe their current experience level in Prompt Engineering "
                    "(beginner/intermediate/advanced or a short sentence about themselves)."
                )
            }
            assistant_reply, error = falcon_chat(st.session_state.chat_history + [system_prompt])
            if error or assistant_reply is None or not assistant_reply.strip():
                st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
            else:
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                st.session_state.stage = "generate_path"
            st.experimental_rerun()
        else:
            sorry_prompt = {
                "role": "system",
                "content": "Thank the user and let them know more skills will be added soon."
            }
            assistant_reply, error = falcon_chat(st.session_state.chat_history + [sorry_prompt])
            if error or assistant_reply is None or not assistant_reply.strip():
                st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
            else:
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
                "The plan should have 5 units. For each unit, provide a short title, a learning objective, and a welcome message. "
                "Respond with valid JSON: [{\"title\":..., \"objective\":..., \"welcome\":...}, ...]"
            )
        }
        plan_json, error = falcon_chat(st.session_state.chat_history + [plan_prompt])
        import json
        try:
            learning_path = json.loads(plan_json)
            st.session_state.learning_path = learning_path
            st.session_state.current_unit = 0
            st.session_state.stage = "in_unit"
            unit = learning_path[0]
            unit_prompt = {
                "role": "system",
                "content": (
                    f"Welcome the user to the first unit: {unit['title']}. {unit['welcome']} "
                    "Invite them to start learning and chatting."
                )
            }
            assistant_reply, error = falcon_chat(st.session_state.chat_history + [unit_prompt])
            if error or assistant_reply is None or not assistant_reply.strip():
                st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
            else:
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            st.experimental_rerun()
        except Exception:
            st.session_state["ai_error"] = "Sorry, something went wrong generating your learning path. Please try again."
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
        assistant_reply, error = falcon_chat(st.session_state.chat_history + [tutor_prompt])
        if error or assistant_reply is None or not assistant_reply.strip():
            st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

            if "[status:pass]" in assistant_reply:
                if st.session_state.current_unit + 1 < len(st.session_state.learning_path):
                    st.session_state.current_unit += 1
                    next_unit = st.session_state.learning_path[st.session_state.current_unit]
                    next_unit_prompt = {
                        "role": "system",
                        "content": (
                            f"Congratulate the user for completing the previous unit and welcome them to the next unit: "
                            f"{next_unit['title']}. {next_unit['welcome']}"
                        )
                    }
                    assistant_reply, error = falcon_chat(st.session_state.chat_history + [next_unit_prompt])
                    if error or assistant_reply is None or not assistant_reply.strip():
                        st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
                    else:
                        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                    st.experimental_rerun()
                else:
                    st.session_state.stage = "path_complete"
                    complete_prompt = {
                        "role": "system",
                        "content": "Congratulate the user for completing all units."
                    }
                    assistant_reply, error = falcon_chat(st.session_state.chat_history + [complete_prompt])
                    if error or assistant_reply is None or not assistant_reply.strip():
                        st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
                    else:
                        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                    st.experimental_rerun()
            elif "[status:stay]" in assistant_reply:
                encourage_prompt = {
                    "role": "system",
                    "content": "Encourage the user to keep working on this unit until they're ready to move on."
                }
                assistant_reply, error = falcon_chat(st.session_state.chat_history + [encourage_prompt])
                if error or assistant_reply is None or not assistant_reply.strip():
                    st.session_state["ai_error"] = error or "AI did not return a reply. Please check your API key or try again later."
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                st.experimental_rerun()

elif st.session_state.stage == "path_complete":
    st.success("You have completed the program! You can start over or review your units.")
    if st.button("Start Over"):
        for k in ("chat_history", "user_info", "selected_skill", "skill_level", "learning_path", "current_unit", "stage", "ai_error"):
            st.session_state[k] = defaults[k]
        st.experimental_rerun()
