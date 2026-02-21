import streamlit as st
import json
import os
from openai import OpenAI

# =========================
# KONFIGURACJA OPENAI
# =========================

# Wklej swój klucz API tutaj:
OPENAI_API_KEY = "TU_WKLEJ_SWÓJ_KLUCZ_API"

client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-4o-mini"

# =========================
# PROMPT SYSTEMOWY
# =========================

SYSTEM_PROMPT = """
You are a scientific Proto-Slavic translator.

Translate into reconstructed Proto-Slavic.

Rules:

• Use standard scientific reconstruction
• Use symbols: ě, ę, ǫ, š, č, ž, ь, ъ
• Preserve morphology
• Use infinitive form for verbs
• Do NOT explain anything
• Output ONLY the Proto-Slavic word or phrase
• No punctuation
• No quotes
• No extra text

Examples:

Polish: usprawiedliwić
Proto-Slavic: opravьdati

Polish: człowiek
Proto-Slavic: čovьkъ

Polish: dom
Proto-Slavic: domъ
"""

# =========================
# FUNKCJA TŁUMACZENIA
# =========================

def translate(text: str) -> str:

    if not text.strip():
        return ""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        max_tokens=50,
    )

    return response.choices[0].message.content.strip()


# =========================
# STREAMLIT UI
# =========================

st.set_page_config(
    page_title="Proto-Slavic Translator",
    page_icon="Ⱄ",
    layout="centered"
)

st.title("Proto-Slavic Translator")
st.caption("Scientific reconstruction")

# session state
if "last_text" not in st.session_state:
    st.session_state.last_text = ""

if "translation" not in st.session_state:
    st.session_state.translation = ""


# input field (auto translate)
text = st.text_input(
    "Polish",
    value=st.session_state.last_text,
    placeholder="np. usprawiedliwić",
    label_visibility="collapsed"
)


# automatyczne tłumaczenie (bez Enter)
if text != st.session_state.last_text:

    st.session_state.last_text = text

    with st.spinner("Translating..."):
        try:
            st.session_state.translation = translate(text)
        except Exception as e:
            st.session_state.translation = f"Error: {e}"


# output
st.text_input(
    "Proto-Slavic",
    value=st.session_state.translation,
    disabled=True,
    label_visibility="collapsed"
)
