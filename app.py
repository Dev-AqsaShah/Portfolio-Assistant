import os
import yaml
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types.generation_types import GenerationConfig

# ---------- Page config ----------
st.set_page_config(page_title="Aqsa Shah Portfolio Assistant", page_icon="🤖", layout="centered")

# ---------- Load API key ----------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")  # ✅ Only from .env

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Settings")
model_name = st.sidebar.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0)
answer_lang = st.sidebar.selectbox("Answer language", ["Urdu + English (default)", "Urdu", "English"], index=0)
temperature = st.sidebar.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.1)
st.sidebar.caption("Tip: Keep temp low to stay closer to the YAML facts.")
if st.sidebar.button("🧹 Clear conversation"):
    st.session_state.pop("chat_history", None)
    st.session_state.pop("system_instruction", None)
    st.rerun()

# ---------- Load profile data ----------
def load_profile(path="aqsa_profile.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

profile = load_profile()

# ---------- Helpers ----------
def build_profile_context(p: dict) -> str:
    def list_join(items):
        return ", ".join(items) if items else ""
    lines = []
    lines.append(f"Name: {p.get('name','')}")
    lines.append(f"Tagline: {p.get('tagline','')}")
    lines.append(f"Location: {p.get('location','')}")
    langs = p.get('languages', [])
    if langs: lines.append("Languages: " + ", ".join(langs))
    if p.get('values'): lines.append("Values: " + list_join(p.get('values', [])))

    edu = p.get('education', [])
    if edu:
        lines.append("Education:")
        for e in edu:
            lines.append(f"- {e.get('program','')} @ {e.get('institution','')} ({e.get('years','')}) {e.get('notes','')}")
    exp = p.get('experience', [])
    if exp:
        lines.append("Experience:")
        for e in exp:
            lines.append(f"- {e.get('role','')} — {e.get('organization','')}; Highlights: " + ", ".join(e.get('highlights', [])))
    sp = p.get('skills_primary', [])
    stools = p.get('skills_tools', [])
    if sp: lines.append("Primary Skills: " + ", ".join(sp))
    if stools: lines.append("Tools: " + ", ".join(stools))

    projects = p.get('projects', [])
    if projects:
        lines.append("Projects:")
        for pr in projects:
            desc = pr.get('description','')
            if p.get('preferences', {}).get('mention_tech_in_project_description', False):
                desc += f" (Tech: {', '.join(pr.get('tech', []))})"
            lines.append(f"- {pr.get('name','')} ({pr.get('year','')}): {desc}")

    ach = p.get('achievements', [])
    if ach:
        lines.append("Achievements:")
        for a in ach:
            lines.append(f"- {a}")

    c = p.get('contact', {})
    if c:
        lines.append("Contact: " + ", ".join([f"{k}: {v}" for k, v in c.items() if v]))
    return "\n".join(lines)

def make_system_instruction(p: dict, lang_choice: str) -> str:
    base_rules = '''
You are Aqsa Shah's portfolio assistant. Answer ONLY using facts from the provided "Aqsa Profile Context".
If a user asks for something not present in the context, reply briefly that you don't have that info and suggest what to add to the profile file.
Never invent dates, counts, employers, or credentials that are not in the context.
Prefer concise, friendly answers with bullet points when listing items.
'''
    urdu = "Reply in easy, friendly Urdu. If something technical is asked, you may mix simple English terms."
    eng = "Reply in clear, simple English."
    mix = "Reply in a friendly mix: start in Urdu, and use simple English terms where helpful."

    lang_block = {"Urdu": urdu, "English": eng, "Urdu + English (default)": mix}.get(lang_choice, mix)

    context = build_profile_context(p)
    sys = f'''{base_rules}
Language style: {lang_block}

=== Aqsa Profile Context (authoritative) ===
{context}
'''
    return sys

# ---------- Configure Gemini ----------
if API_KEY:
    genai.configure(api_key=API_KEY)

system_instruction = make_system_instruction(profile, answer_lang)

if "system_instruction" not in st.session_state or st.session_state["system_instruction"] != system_instruction:
    st.session_state["system_instruction"] = system_instruction
    st.session_state["chat_history"] = []

# ---------- Header ----------
st.title(" Aqsa Shah — Portfolio Assistant")
st.caption("Ask me anything about Aqsa (skills, education, projects, achievements). I answer only from Aqsa's profile.")

# ---------- Preset buttons ----------
st.write("Try:")
cols = st.columns(3)
with cols[0]:
    if st.button("Which skills does Aqsa have?"):
        st.session_state["preset"] = "Which skills does Aqsa have?"
with cols[1]:
    if st.button("Tell me about her projects."):
        st.session_state["preset"] = "Tell me about her projects."
with cols[2]:
    if st.button("Where did she study?"):
        st.session_state["preset"] = "Where did she study?"

# ---------- Chat input ----------
user_msg = st.chat_input("Type your question…")
if "preset" in st.session_state:
    user_msg = st.session_state.pop("preset")

for role, content in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.markdown(content)

if not API_KEY:
    st.warning("⚠️ Add your Gemini API key in `.env` file as GEMINI_API_KEY=your_key_here")
else:
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
        generation_config=GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=32,
            max_output_tokens=1024,
        ),
        safety_settings=None,
    )

    if user_msg:
        st.session_state["chat_history"].append(("user", user_msg))
        with st.chat_message("user"):
            st.markdown(user_msg)

        history_text = ""
        for r, c in st.session_state["chat_history"][-6:]:
            history_text += f"{r.upper()}: {c}\n"

        prompt = f'''Using only the Aqsa Profile Context in your system instruction, answer the USER.
Keep the reply concise and friendly. If a fact is missing, say you don't have it.

Chat (recent turns):
{history_text}
'''
        try:
            resp = model.generate_content(prompt)
            reply_text = resp.text or "(No response)"
        except Exception as e:
            reply_text = f"Sorry, I hit an error talking to the model: {e!s}"

        st.session_state["chat_history"].append(("assistant", reply_text))
        with st.chat_message("assistant"):
            st.markdown(reply_text)
