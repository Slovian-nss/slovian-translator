import streamlit as st
import json
import os
import re
import requests
import base64
from collections import defaultdict

# --- KONFIGURACJA GITHUB ---
GITHUB_TOKEN = "MYTOKEN"
REPO_OWNER = "Slovian-nss"
REPO_NAME = "slovian-translator"
FILE_PATH = "selflearning.json"
BRANCH = "main"

LANGUAGES = {
    "pl": "Polski",
    "sl": "Prasłowiański",
    "en": "Angielski",
    "de": "Niemiecki",
    "fr": "Francuski",
    "es": "Hiszpański",
    "ru": "Rosyjski"
}

st.set_page_config(page_title="DeepL Slověnьsk", layout="wide")

# --- ZARZĄDZANIE STANEM (Session State) ---
if 'src_lang' not in st.session_state:
    st.session_state.src_lang = "pl"
if 'tgt_lang' not in st.session_state:
    st.session_state.tgt_lang = "sl"
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""

# --- STYLIZACJA UI ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; color: #1a1a1b; }
    
    /* Wyraźne, ciemne obramowania pól */
    .stTextArea textarea, div[data-baseweb="select"] { 
        border: 2px solid #2d3748 !important; 
        border-radius: 10px !important; 
        background-color: white !important;
        color: #1a1a1b !important;
    }

    /* Kontener dla przycisku zamiany */
    .swap-btn-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        margin-top: 2px;
    }
    
    .stButton button {
        background-color: #002b49; 
        color: white; 
        border-radius: 8px; 
        border: none; 
        width: 50px;
        height: 40px;
        font-weight: bold;
    }
    .stButton button:hover { background-color: #004a7c; color: white; border: none; }
    
    h1 { color: #002b49; font-weight: 800; text-align: center; margin-bottom: 20px; }
    .stCaption { text-align: center; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA DANYCH I TŁUMACZENIA ---
def get_github_file():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return json.loads(content), data['sha']
    except:
        pass
    return [], None

@st.cache_data
def load_all_data():
    osnova = []
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    sl, _ = get_github_file()
    return osnova + sl

all_data = load_all_data()

@st.cache_data
def build_dictionaries(data):
    pl_sl = defaultdict(list); sl_pl = defaultdict(list)
    for e in data:
        pl, sl = e.get("polish","").lower().strip(), e.get("slovian","").lower().strip()
        if pl: pl_sl[pl].append(e.get("slovian",""))
        if sl: sl_pl[sl].append(e.get("polish",""))
    return pl_sl, sl_pl

pl_to_sl, sl_to_pl = build_dictionaries(all_data)

def external_api_translate(text, src, tgt):
    if src == tgt: return text
    # MyMemory API - darmowe i bez klucza dla małego ruchu
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={src}|{tgt}"
    try:
        r = requests.get(url, timeout=5).json()
        return r['responseData']['translatedText']
    except:
        return text

def local_slovian_logic(text, to_sl=True):
    dic = pl_to_sl if to_sl else sl_to_pl
    def repl(m):
        w = m.group(0); lw = w.lower()
        if lw in dic and dic[lw]:
            t = dic[lw][0]
            if w.isupper(): return t.upper()
            if w[0].isupper(): return t.capitalize()
            return t
        return f"[{w}]" if to_sl else w
    return re.sub(r'\w+', repl, text)

def translate_engine(text, src, tgt):
    if not text.strip(): return ""
    # Jeśli celem jest prasłowiański
    if tgt == "sl":
        pivot_pl = external_api_translate(text, src, "pl") if src != "pl" else text
        return local_slovian_logic(pivot_pl, to_sl=True)
    # Jeśli źródłem jest prasłowiański
    elif src == "sl":
        pivot_pl = local_slovian_logic(text, to_sl=False)
        return external_api_translate(pivot_pl, "pl", tgt) if tgt != "pl" else pivot_pl
    # Inne języki (bezpośrednio przez API)
    else:
        return external_api_translate(text, src, tgt)

# --- FUNKCJA ZAMIANY (SWAP) ---
def swap_languages():
    # Pobieramy obecny wynik, by stał się nowym wejściem
    current_input = st.session_state.input_text
    current_output = translate_engine(current_input, st.session_state.src_lang, st.session_state.tgt_lang)
    
    # Zamiana
    old_src = st.session_state.src_lang
    st.session_state.src_lang = st.session_state.tgt_lang
    st.session_state.tgt_lang = old_src
    st.session_state.input_text = current_output

# --- INTERFEJS UŻYTKOWNIKA ---
st.title("DeepL Slověnьsk")

# Wiersz 1: Wybór Języka i Przycisk Swap
col_l1, col_sw, col_l2 = st.columns([10, 1, 10])

with col_l1:
    src_lang = st.selectbox("Z", options=list(LANGUAGES.keys()), 
                            format_func=lambda x: LANGUAGES[x], 
                            key="src_lang", label_visibility="collapsed")

with col_sw:
    st.markdown('<div class="swap-btn-container">', unsafe_allow_html=True)
    if st.button("⇄", on_click=swap_languages):
        pass # Logika jest w on_click
    st.markdown('</div>', unsafe_allow_html=True)

with col_l2:
    tgt_lang = st.selectbox("Na", options=list(LANGUAGES.keys()), 
                            format_func=lambda x: LANGUAGES[x], 
                            key="tgt_lang", label_visibility="collapsed")

# Wiersz 2: Pola Tekstowe
col_t1, col_sp, col_t2 = st.columns([10, 1, 10])

with col_t1:
    input_text = st.text_area("Tekst", value=st.session_state.input_text, 
                              placeholder="Wpisz tekst...", height=350, 
                              key="input_area", label_visibility="collapsed")
    # Synchronizacja tekstu z session_state
    st.session_state.input_text = input_text

with col_t2:
    output_text = ""
    if st.session_state.input_text:
        with st.spinner('Tłumaczenie...'):
            output_text = translate_engine(st.session_state.input_text, 
                                          st.session_state.src_lang, 
                                          st.session_state.tgt_lang)
    
    st.text_area("Wynik", value=output_text, height=350, 
                 key="output_area", label_visibility="collapsed", disabled=False)

st.markdown("---")
st.caption("Standardowa baza Prasłowiańska + API MyMemory (Pivot: Polski)")
