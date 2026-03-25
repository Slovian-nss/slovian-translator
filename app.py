import streamlit as st
import json
import re
from deep_translator import GoogleTranslator
from streamlit_javascript import st_javascript

# ================== 1. KONFIGURACJA STRONY ==================
st.set_page_config(page_title="Slovo Translator", layout="wide")

# ================== 2. TŁUMACZENIA INTERFEJSU (UI) ==================
UI_DATA = {
    "pl": {
        "title": "Tłumacz", "from": "Z języka:", "to": "Na język:", 
        "input": "Wpisz tekst:", "btn": "🔄 Tłumacz", "res": "Wynik:", 
        "warn": "⚠️ Wpisz tekst.", "auto": "Automatyczny", "slo": "Słowiański"
    },
    "en": {
        "title": "Translator", "from": "From:", "to": "To:", 
        "input": "Enter text:", "btn": "🔄 Translate", "res": "Result:", 
        "warn": "⚠️ Please enter text.", "auto": "Auto", "slo": "Slovian"
    },
    "de": {
        "title": "Übersetzer", "from": "Von:", "to": "Nach:", 
        "input": "Text eingeben:", "btn": "🔄 Übersetzen", "res": "Ergebnis:", 
        "warn": "⚠️ Text eingeben.", "auto": "Automatisch", "slo": "Slowianisch"
    },
    "fr": {
        "title": "Traducteur", "from": "De:", "to": "Vers:", 
        "input": "Entrez le texte:", "btn": "🔄 Traduire", "res": "Résultat:", 
        "warn": "⚠️ Entrez le texte.", "auto": "Auto", "slo": "Slovène (Slo)"
    },
    "es": {
        "title": "Traductor", "from": "De:", "to": "A:", 
        "input": "Ingrese texto:", "btn": "🔄 Traducir", "res": "Resultado:", 
        "warn": "⚠️ Ingrese texto.", "auto": "Auto", "slo": "Esloviano"
    }
}

# ================== 3. DETEKCJA JĘZYKA URZĄDZENIA ==================
if "lang_code" not in st.session_state:
    # Pobieramy język z przeglądarki użytkownika
    js_lang = st_javascript("window.navigator.language")
    if js_lang:
        detected = js_lang[:2].lower()
        st.session_state.lang_code = detected if detected in UI_DATA else "en"
    else:
        # Domyślnie angielski, dopóki JS nie odpowie
        st.session_state.lang_code = "en"

ui = UI_DATA[st.session_state.lang_code]

# ================== 4. OBSŁUGA JĘZYKÓW GOOGLE ==================
@st.cache_resource
def get_google_languages():
    try:
        langs = GoogleTranslator().get_supported_languages(as_dict=True)
        return {name.capitalize(): code for name, code in langs.items()}
    except:
        return {"Polish": "pl", "English": "en", "German": "de"}

GOOGLE_LANGS = get_google_languages()

# Budujemy listę opcji dynamicznie na podstawie języka UI
ALL_OPTIONS = {
    ui["auto"]: "auto",
    ui["slo"]: "slo",
    **GOOGLE_LANGS
}

# ================== 5. PERSISTENCJA (localStorage) ==================
def get_persisted_target():
    code = st_javascript("localStorage.getItem('slovo_target_lang');")
    return code if code in ALL_OPTIONS.values() else 'slo'

def save_target(lang_code):
    st_javascript(f"localStorage.setItem('slovo_target_lang', '{lang_code}');")

# Style CSS
st.markdown("""
    <style>
    .main { max-width: 900px; margin: 0 auto; }
    .stTextArea textarea { font-size: 1.1rem; }
    label { font-weight: 600 !important; margin-bottom: 0.3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ================== 6. LOGIKA SŁOWNIKA SŁOWIAŃSKIEGO ==================
@st.cache_data
def load_json_safe(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

osnova = load_json_safe("osnova.json")
vuzor = load_json_safe("vuzor.json")

@st.cache_data
def build_dict(osnova, vuzor):
    pl_to_slo = {}
    slo_to_pl = {}
    for entry in osnova + vuzor:
        pol = entry.get("polish", "").lower().strip()
        slo = entry.get("slovian", "").strip()
        if pol and slo:
            pl_to_slo[pol] = slo
            slo_to_pl[slo.lower()] = pol
    return pl_to_slo, slo_to_pl

pl_to_slo, slo_to_pl = build_dict(osnova, vuzor)

def translate_pl_to_slo(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []
    for t in tokens:
        low = t.lower()
        if low in pl_to_slo:
            res = pl_to_slo[low]
            if t.istitle(): res = res.capitalize()
            elif t.isupper(): res = res.upper()
            result.append(res)
        else:
            result.append(t)
    return "".join(result)

def google_translate(text, src, tgt):
    try:
        return GoogleTranslator(source=src, target=tgt).translate(text)
    except Exception as e:
        return f"(Error: {e})"

# ================== 7. INTERFEJS UŻYTKOWNIKA ==================
st.write(f"### 🌐 Slovo ({st.session_state.lang_code.upper()})")
st.title(ui["title"])

col1, col2 = st.columns(2)

with col1:
    st.selectbox(ui["from"], list(ALL_OPTIONS.keys()), index=0, key="src_key")

with col2:
    persisted = get_persisted_target()
    all_vals = list(ALL_OPTIONS.values())
    try:
        default_idx = all_vals.index(persisted)
    except:
        default_idx = 1
    st.selectbox(ui["to"], list(ALL_OPTIONS.keys()), index=default_idx, key="tgt_key")

# Zapisywanie wyboru do pamięci przeglądarki
current_tgt_code = ALL_OPTIONS[st.session_state.tgt_key]
save_target(current_tgt_code)

user_input = st.text_area(ui["input"], height=150, placeholder="...")

if st.button(ui["btn"], type="primary"):
    if user_input.strip():
        src_code = ALL_OPTIONS[st.session_state.src_key]
        tgt_code = ALL_OPTIONS[st.session_state.tgt_key]
        
        with st.spinner('...'):
            if tgt_code == "slo":
                # Tłumaczenie NA Słowiański
                pl_text = google_translate(user_input, src_code, "pl") if src_code != "pl" else user_input
                result = translate_pl_to_slo(pl_text)
            elif src_code == "slo":
                # Tłumaczenie ZE Słowiańskiego
                tokens = re.findall(r'\w+|[^\w\s]|\s+', user_input)
                pl_text = "".join([slo_to_pl.get(t.lower(), t) for t in tokens])
                result = google_translate(pl_text, "pl", tgt_code)
            else:
                # Standardowe Google -> Google
                result = google_translate(user_input, src_code, tgt_code)
            
            st.divider()
            st.markdown(f"### {ui['res']}")
            st.success(result)
    else:
        st.warning(ui["warn"])
