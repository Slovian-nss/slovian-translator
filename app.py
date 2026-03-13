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

    /* Wycentrowanie przycisku SWAP w osi list wyboru */
    .swap-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding-top: 1px; /* Precyzyjne dopasowanie do linii pól */
    }
    
    .stButton button {
        background-color: #002b49; 
        color: white; 
        border-radius: 8px; 
        border: none; 
        width: 100%;
        height: 42px;
        font-weight: bold;
    }
    .stButton button:hover { background-color: #004a7c; color: white; border: none; }
    
    h1 { color: #002b49; font-weight: 800; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA POBIERANIA DANYCH ---
@st.cache_data(ttl=60)
def load_all_data():
    osnova = []
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    
    # Próba pobrania z GitHub
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            content = base64.b64decode(res.json()['content']).decode('utf-8')
            osnova += json.loads(content)
    except:
        pass
    return osnova

all_data = load_all_data()

@st.cache_data
def build_dictionaries(data):
    pl_sl = defaultdict(list); sl_pl = defaultdict(list)
    for e in data:
        pl, sl = e.get("polish","").lower().strip(), e.get("slovian","").lower().strip()
        if pl and sl:
            pl_sl[pl].append(sl)
            sl_pl[sl].append(pl)
    return pl_sl, sl_pl

pl_to_sl, sl_to_pl = build_dictionaries(all_data)

# --- SILNIK TŁUMACZENIA ---
def external_api_translate(text, src, tgt):
    if src == tgt: return text
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={src}|{tgt}"
    try:
        r = requests.get(url, timeout=5).json()
        return r['responseData']['translatedText']
    except:
        return text

def local_slovian_logic(text, to_sl=True):
    dic = pl_to_sl if to_sl else sl_to_pl
    if not dic: return text
    
    # Dzielenie na słowa i znaki interpunkcyjne
    tokens = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    result = []
    
    for token in tokens:
        l_token = token.lower()
        if l_token in dic:
            translated = dic[l_token][0]
            if token.isupper(): translated = translated.upper()
            elif token[0].isupper(): translated = translated.capitalize()
            result.append(translated)
        else:
            result.append(f"[{token}]" if to_sl and token.isalnum() else token)
    
    return "".join([" " + t if t.isalnum() and i > 0 and result[i-1].isalnum() else t for i, t in enumerate(result)])

def master_translate(text, src, tgt):
    if not text.strip(): return ""
    if tgt == "sl":
        pivot = external_api_translate(text, src, "pl") if src != "pl" else text
        return local_slovian_logic(pivot, to_sl=True)
    elif src == "sl":
        pivot = local_slovian_logic(text, to_sl=False)
        return external_api_translate(pivot, "pl", tgt) if tgt != "pl" else pivot
    else:
        return external_api_translate(text, src, tgt)

# --- SESSION STATE ---
if 'src_lang' not in st.session_state: st.session_state.src_lang = "pl"
if 'tgt_lang' not in st.session_state: st.session_state.tgt_lang = "sl"
if 'input_text' not in st.session_state: st.session_state.input_text = ""

def swap_action():
    # Pobierz aktualne tłumaczenie przed zamianą
    current_out = master_translate(st.session_state.input_text, st.session_state.src_lang, st.session_state.tgt_lang)
    # Zamień języki
    old_src = st.session_state.src_lang
    st.session_state.src_lang = st.session_state.tgt_lang
    st.session_state.tgt_lang = old_src
    # Tekst wynikowy staje się nowym wejściem
    st.session_state.input_text = current_out

# --- UI ---
st.title("DeepL Slověnьsk")

# Wiersz wyboru języków
c1, c_sw, c2 = st.columns([10, 1, 10])

with c1:
    st.selectbox("Źródło", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="src_lang", label_visibility="collapsed")

with c_sw:
    st.markdown('<div class="swap-container">', unsafe_allow_html=True)
    st.button("⇄", on_click=swap_action)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.selectbox("Cel", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="tgt_lang", label_visibility="collapsed")

# Wiersz pól tekstowych
t1, t_space, t2 = st.columns([10, 1, 10])

with t1:
    # Używamy on_change do natychmiastowej aktualizacji
    st.text_area("Input", key="input_text", height=350, label_visibility="collapsed", placeholder="Wpisz tekst tutaj...")

with t2:
    translated = master_translate(st.session_state.input_text, st.session_state.src_lang, st.session_state.tgt_lang)
    st.text_area("Output", value=translated, height=350, label_visibility="collapsed", disabled=False)

st.markdown("---")
st.caption("Jeśli słowo nie istnieje w bazie prasłowiańskiej, pojawi się w nawiasie [słowo].")
