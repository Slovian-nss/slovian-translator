import streamlit as st
import json
import os
import re
import requests
import base64
from collections import defaultdict

# --- KONFIGURACJA ---

LANGUAGES = {
"pl": "Polski",
"sl": "Prasłowiański",
"en": "Angielski",
"de": "Niemiecki",
"fr": "Francuski",
"es": "Hiszpański",
"ru": "Rosyjski"
}

st.set_page_config(page_title="Tłumacz Języka Słowiańskiego", layout="wide")

# --- CSS ---

st.markdown("""

<style>

.stApp{
background:#f0f2f5;
}

.title-text{
color:#002b49;
font-weight:800;
text-align:center;
font-size:2.2rem;
margin-top:-20px;
margin-bottom:25px;
}

div[data-baseweb="select"]{
border:2px solid #2d3748 !important;
border-radius:10px !important;
background:white !important;
}

.stTextArea textarea{
border:2px solid #2d3748 !important;
border-radius:10px !important;
background:white !important;
}

.swap-btn{
margin-top:28px;
}

.swap-btn button{
height:42px !important;
width:100%;
font-size:18px;
}

.stButton button{
background:#002b49;
color:white !important;
border-radius:8px;
border:none;
font-weight:bold;
}

</style>

""", unsafe_allow_html=True)

# --- SILNIK TŁUMACZENIA ---

def translate_engine(text, src, tgt):

```
if not text.strip():
    return ""

# tutaj podłączysz swój prawdziwy silnik tłumaczenia
return text
```

# --- SESSION STATE ---

if "input_text" not in st.session_state:
st.session_state.input_text = ""

if "src_lang" not in st.session_state:
st.session_state.src_lang = "pl"

if "tgt_lang" not in st.session_state:
st.session_state.tgt_lang = "sl"

def swap_languages():
st.session_state.src_lang, st.session_state.tgt_lang = (
st.session_state.tgt_lang,
st.session_state.src_lang
)

# --- TYTUŁ ---

st.markdown(
'<h1 class="title-text">Tłumacz Języka Słowiańskiego (Prasłowiańskiego)</h1>',
unsafe_allow_html=True
)

# --- WYBÓR JĘZYKÓW ---

col_l, col_s, col_r = st.columns([10,1.2,10])

with col_l:
st.selectbox(
"",
options=list(LANGUAGES.keys()),
format_func=lambda x: LANGUAGES[x],
key="src_lang",
label_visibility="collapsed"
)

with col_s:
st.markdown('<div class="swap-btn">', unsafe_allow_html=True)
st.button("⇄", on_click=swap_languages, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

with col_r:
st.selectbox(
"",
options=list(LANGUAGES.keys()),
format_func=lambda x: LANGUAGES[x],
key="tgt_lang",
label_visibility="collapsed"
)

st.write("")

# --- PRZYCISKI KOPIOWANIA ---

cp_l, cp_mid, cp_r = st.columns([10,1.2,10])

with cp_l:
st.button("📋 Kopiuj")

with cp_r:
st.button("📋 Kopiuj wynik")

# --- POLA TEKSTOWE ---

t_l, t_mid, t_r = st.columns([10,1.2,10])

with t_l:

```
input_txt = st.text_area(
    "",
    value=st.session_state.input_text,
    height=350,
    placeholder="Wpisz tekst do przetłumaczenia..."
)

st.session_state.input_text = input_txt
```

with t_r:

```
wynik = translate_engine(
    st.session_state.input_text,
    st.session_state.src_lang,
    st.session_state.tgt_lang
)

st.text_area(
    "",
    value=wynik,
    height=350
)
```

st.markdown("---")
st.caption("Interfejs zoptymalizowany pod kątem estetyki DeepL.")
