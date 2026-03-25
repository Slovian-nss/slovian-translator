import streamlit as st
import json
import re
from deep_translator import GoogleTranslator
from streamlit_javascript import st_javascript

# ================== 1. DYNAMICZNE POBIERANIE JĘZYKÓW ==================
@st.cache_resource
def get_all_languages():
    try:
        langs = GoogleTranslator().get_supported_languages(as_dict=True)
        return {name.capitalize(): code for name, code in langs.items()}
    except:
        return {"Polish": "pl", "English": "en", "German": "de"}

GOOGLE_LANGS = get_all_languages()
ALL_OPTIONS = {"Auto": "auto", "Słowiański": "slo", **GOOGLE_LANGS}

# ================== 2. DETEKCJA JĘZYKA UI ==================
st_lang = st_javascript("window.navigator.language")
UI_TRANSLATIONS = {
    "pl": {"title": "Tłumacz", "from": "Z języka:", "to": "Na język:", "input": "Wpisz tekst:", "btn": "🔄 Tłumacz", "res": "Wynik:", "warn": "⚠️ Wpisz tekst."},
    "en": {"title": "Translator", "from": "From:", "to": "To:", "input": "Enter text:", "btn": "🔄 Translate", "res": "Result:", "warn": "⚠️ Please enter text."},
    "de": {"title": "Übersetzer", "from": "Von:", "to": "Nach:", "input": "Text eingeben:", "btn": "🔄 Übersetzen", "res": "Ergebnis:", "warn": "⚠️ Text eingeben."},
    "fr": {"title": "Traducteur", "from": "De:", "to": "Vers:", "input": "Entrez le texte:", "btn": "🔄 Traduire", "res": "Résultat:", "warn": "⚠️ Entrez le texte."},
    "es": {"title": "Traductor", "from": "De:", "to": "A:", "input": "Ingrese texto:", "btn": "🔄 Traducir", "res": "Resultado:", "warn": "⚠️ Ingrese texto."}
}

if st_lang:
    detected_code = st_lang[:2].lower()
    lang_code = detected_code if detected_code in UI_TRANSLATIONS else "en"
else:
    lang_code = "pl"
ui = UI_TRANSLATIONS[lang_code]

# ================== 3. PERSISTENCJA ==================
def get_persisted_target():
    code = st_javascript("""
        let val = localStorage.getItem('slovo_target_lang');
        return val !== null ? val : 'slo';
    """)
    return code if code in ALL_OPTIONS.values() else 'slo'

def save_target(lang_code):
    st_javascript(f"localStorage.setItem('slovo_target_lang', '{lang_code}');")

# ================== 4. KONFIGURACJA ==================
st.set_page_config(page_title=ui["title"], layout="wide")
st.markdown("""
    <style>
    .main { max-width: 900px; margin: 0 auto; }
    .stTextArea textarea { font-size: 1.1rem; }
    div[data-testid="column"] > div { gap: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# ================== 5. LOGIKA SŁOWIAŃSKA (bez zmian) ==================
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

# ================== 6. INTERFEJS ==================
st.write("### 🌐 Slovo")
st.title(ui["title"])

col1, col2 = st.columns(2)

with col1:
    st.selectbox(ui["from"], list(ALL_OPTIONS.keys()), index=0, key="src")

with col2:
    persisted = get_persisted_target()
    try:
        default_idx = list(ALL_OPTIONS.values()).index(persisted)
    except ValueError:
        default_idx = list(ALL_OPTIONS.values()).index("slo")
    st.selectbox(ui["to"], list(ALL_OPTIONS.keys()), index=default_idx, key="target_lang")

if "target_lang" in st.session_state:
    save_target(ALL_OPTIONS[st.session_state.target_lang])

user_input = st.text_area(ui["input"], height=150, placeholder="...")

if st.button(ui["btn"], type="primary"):
    if user_input.strip():
        src_code = ALL_OPTIONS[st.session_state.src]
        tgt_code = ALL_OPTIONS[st.session_state.target_lang]
        with st.spinner('...'):
            if tgt_code == "slo":
                pl_text = google_translate(user_input, src_code, "pl") if src_code != "pl" else user_input
                result = translate_pl_to_slo(pl_text)
            elif src_code == "slo":
                tokens = re.findall(r'\w+|[^\w\s]|\s+', user_input)
                pl_text = "".join([slo_to_pl.get(t.lower(), t) for t in tokens])
                result = google_translate(pl_text, "pl", tgt_code)
            else:
                result = google_translate(user_input, src_code, tgt_code)
            st.divider()
            st.markdown(f"### {ui['res']}")
            st.success(result)
    else:
        st.warning(ui["warn"])
