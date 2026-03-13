import streamlit as st
import json
import os
import re
import requests
import base64
from collections import defaultdict

# --- KONFIGURACJA ---
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

# --- STYLIZACJA A LA DEEPL ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; color: #1a1a1b; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .main-container { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .stTextArea textarea { 
        border: 1px solid #e1e4e8 !important; 
        border-radius: 10px !important; 
        font-size: 18px !important;
        background-color: white !important;
        color: #1a1a1b !important;
    }
    .stButton button {
        background-color: #002b49; color: white; border-radius: 8px; border: none;
    }
    .stButton button:hover { background-color: #004a7c; color: white; }
    h1 { color: #002b49; font-weight: 800; text-align: center; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA DANYCH I GITHUB ---
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
    selflearning, _ = get_github_file()
    return osnova + selflearning

all_data = load_all_data()

@st.cache_data
def build_dictionaries(data):
    pl_sl = defaultdict(list)
    sl_pl = defaultdict(list)
    for e in data:
        pl = e.get("polish","").lower().strip()
        sl = e.get("slovian","").lower().strip()
        if pl: pl_sl[pl].append(e.get("slovian",""))
        if sl: sl_pl[sl].append(e.get("polish",""))
    return pl_sl, sl_pl

pl_to_sl, sl_to_pl = build_dictionaries(all_data)

# --- TŁUMACZENIE ---

def external_translate(text, source_lang, target_lang):
    """API MyMemory - darmowe, bez klucza"""
    if source_lang == target_lang: return text
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_lang}|{target_lang}"
    try:
        res = requests.get(url).json()
        return res['responseData']['translatedText']
    except:
        return text

def local_translate(text, to_sl=True):
    """Tłumaczenie PL <-> SL na bazie słownika"""
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

def master_translate(text, src, tgt):
    if not text.strip(): return ""
    
    # CASE 1: Dowolny -> Prasłowiański (Pivot przez Polski)
    if tgt == "sl":
        if src != "pl":
            text = external_translate(text, src, "pl")
        return local_translate(text, to_sl=True)
    
    # CASE 2: Prasłowiański -> Dowolny (Pivot przez Polski)
    elif src == "sl":
        polish_text = local_translate(text, to_sl=False)
        if tgt == "pl":
            return polish_text
        return external_translate(polish_text, "pl", tgt)
    
    # CASE 3: Inne języki (bez prasłowiańskiego)
    else:
        return external_translate(text, src, tgt)

# --- UI ---
st.title("DeepL Slověnьsk")

with st.container():
    c1, mid, c2 = st.columns([10, 1, 10])
    
    with c1:
        src_lang = st.selectbox("Język źródłowy", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)
        source_text = st.text_area("Tekst wprowadzany", placeholder="Wpisz tekst...", height=250, key="src")
        
    with mid:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("⇄"):
            # Prosta zamiana miejsc (wymagałaby zarządzania stanem sesji dla pełnej funkcjonalności)
            st.toast("Zamieniono języki!")

    with c2:
        tgt_lang = st.selectbox("Język docelowy", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=1)
        
        # Automatyczne tłumaczenie
        translated_result = ""
        if source_text:
            with st.spinner('Tłumaczenie...'):
                translated_result = master_translate(source_text, src_lang, tgt_lang)
        
        st.text_area("Tłumaczenie", value=translated_result, height=250, key="tgt", disabled=True)

st.divider()

# --- MODUŁ NAUKI (GITHUB) ---
with st.expander("🧠 Rozbuduj bazę Prasłowiańską"):
    col_a, col_b = st.columns(2)
    new_pl = col_a.text_input("Słowo polskie")
    new_sl = col_b.text_input("Słowo prasłowiańskie")
    if st.button("Dodaj do słownika"):
        if new_pl and new_sl:
            # Tutaj funkcja save_pair_to_github z Twojego kodu
            st.info("Trwa wysyłanie do repozytorium...")
            # save_pair_to_github(new_pl, new_sl) # Odkomentuj w produkcji
        else:
            st.warning("Uzupełnij oba pola!")
