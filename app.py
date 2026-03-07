import streamlit as st
import json
import os
import re
from groq import Groq

# ================== 1. KONFIGURACJA WIZUALNA ==================
st.set_page_config(page_title="Ekspercki Perkladačь", layout="wide")

st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stTextInput input {background-color: #1a1a1a; color: #dcdcdc; border-radius: 8px;}
    .stSuccess {background-color: #152b1b; color: #4ade80; border: 1px solid #22c55e;}
    .debug-box {background-color: #262730; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.85rem;}
</style>
""", unsafe_allow_html=True)

# ================== 2. POŁĄCZENIE Z API ==================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Błąd: Brak klucza GROQ_API_KEY w st.secrets.")
    st.stop()

# ================== 3. BEZPIECZNY SILNIK DANYCH ==================
@st.cache_data
def load_full_database():
    def read_json_safe(path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Filtrujemy tylko słowniki, aby uniknąć błędów typu 'list indices must be integers'
                return [item for item in data if isinstance(item, dict)]
        except Exception as e:
            st.warning(f"Problem z plikiem {path}: {e}")
            return []
    
    return read_json_safe("osnova.json"), read_json_safe("vuzor.json")

osnova_db, vuzor_db = load_full_database()

# ================== 4. LOGIKA MAPOWANIA MORFOLOGICZNEGO ==================

def translate_logic(text):
    # KROK A: AI jako analityk gramatyczny (nie tłumacz!)
    # Prosimy AI o rozbicie zdania na parametry, które rozpozna nasz skrypt
    analysis_prompt = f"""Analyze the following Polish sentence for translation.
For each word return ONLY a line in format: polish_word | case | number | gender
Use these English tags:
- Cases: nominative, genitive, dative, accusative, instrumental, locative, vocative
- Number: singular, plural
- Gender: masculine, feminine, neuter

Sentence: {text}"""

    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0
        )
        raw_analysis = chat_completion.choices[0].message.content
    except Exception as e:
        return f"Błąd komunikacji z AI: {e}", []

    final_sentence = []
    logs = []

    # KROK B: Przetwarzanie linii po linii
    lines = raw_analysis.strip().split('\n')
    for line in lines:
        if "|" not in line: continue
        
        # Oczyszczanie danych z analizy
        parts = [p.strip().lower() for p in line.split('|')]
        if len(parts) < 3: continue
        
        pl_word = re.sub(r'[^\w\s]', '', parts[0]) # usunięcie interpunkcji
        target_case = parts[1]
        target_number = parts[2]

        # 1. Znajdź rdzeń (slovian) w osnova.json
        slov_root = None
        for entry in osnova_db:
            if entry.get('polish', '').lower() == pl_word:
                slov_root = entry.get('slovian')
                break
        
        # 2. Jeśli znaleźliśmy rdzeń, szukamy DOKŁADNEJ formy w vuzor.json
        if slov_root:
            matched_form = None
            for pattern in vuzor_db:
                info_text = pattern.get("type and case", "").lower()
                form_value = pattern.get("slovian", "")
                
                # Warunki: słowo bazowe musi być w opisie, a przypadek i liczba muszą się zgadzać
                if (f"'{slov_root}'" in info_text or slov_root == pattern.get("slovian")) \
                   and target_case in info_text \
                   and target_number in info_text:
                    matched_form = form_value
                    break
            
            if matched_form:
                final_sentence.append(matched_form)
                logs.append(f"✅ DOPASOWANO: {pl_word} -> {matched_form} ({target_case}, {target_number})")
            else:
                # Jeśli brak w vuzor, bierzemy formę bazową z oznaczeniem
                final_sentence.append(f"{slov_root}*")
                logs.append(f"⚠️ BRAK ODMIAY: Znaleziono rdzeń '{slov_root}', ale brak formy dla {target_case} {target_number}")
        else:
            # Obsługa przyimków i słów statycznych (w, na, i, etc.)
            statics = {"w": "vu", "na": "na", "z": "iz", "za": "za", "i": "i", "a": "a"}
            replacement = statics.get(pl_word, pl_word)
            final_sentence.append(replacement)
            logs.append(f"ℹ️ STATYCZNE/BRAK: {pl_word} -> {replacement}")

    return " ".join(final_sentence).capitalize(), logs

# ================== 5. INTERFEJS UŻYTKOWNIKA ==================

st.title("🏛️ Ekspercki Perkladačь (Hoenir Engine)")
st.markdown("System mapowania morfologicznego: **LLM Analysis + Python Table Mapping**")

input_text = st.text_input("Wpisz polskie zdanie do przetłumaczenia:", value="W Słowianach siła.")

if input_text:
    with st.spinner("Trwa analiza morfologiczna i przeszukiwanie tabel..."):
        translated_text, debug_logs = translate_logic(input_text)
        
        st.write("### Wynik tłumaczenia:")
        st.success(translated_text)
        
        with st.expander("Szczegóły techniczne mapowania (Logi silnika)"):
            for log in debug_logs:
                st.markdown(f"<div class='debug-box'>{log}</div>", unsafe_allow_html=True)

# Stopka informacyjna
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption(f"Baza rdzeni (osnova.json): {len(osnova_db)} rekordów")
with col2:
    st.caption(f"Baza odmian (vuzor.json): {len(vuzor_db)} rekordów")
