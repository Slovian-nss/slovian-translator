import streamlit as st
import json
import os
import re
from groq import Groq

# ================== 1. KONFIGURACJA I MAPOWANIE ZNAKÓW ==================
st.set_page_config(page_title="Ekspercki Perkladačь (Hoenir Engine)", layout="wide")

# Tabela konwersji znaków (Normalizacja orthografii na słowiańską)
ORTHO_MAP = {
    'ą': 'ę', 'ć': 'ć', 'ę': 'ę', 'ł': 'l', 'ń': 'n', 
    'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z'
}

def normalize_to_slovian(text):
    """Zamienia polskie znaki na ich słowiańskie odpowiedniki zgodnie z bazą."""
    for pl, sl in ORTHO_MAP.items():
        text = text.replace(pl, sl)
    return text

# ================== 2. POŁĄCZENIE Z API ==================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Błąd: Brak klucza GROQ_API_KEY.")
    st.stop()

# ================== 3. ŁADOWANIE DANYCH (ZABEZPIECZONE) ==================
@st.cache_data
def load_full_database():
    def read_json_safe(path):
        if not os.path.exists(path): return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [item for item in data if isinstance(item, dict)]
    return read_json_safe("osnova.json"), read_json_safe("vuzor.json")

osnova_db, vuzor_db = load_full_database()

# ================== 4. SILNIK LOGICZNY HOENIRA ==================

def hoenir_engine(text):
    # KROK 1: Analiza morfologiczna (AI tylko taguje gramatykę)
    analysis_prompt = f"""Analyze the Polish sentence. 
Return ONLY: polish_word | case | number | gender | person | tense
Tags: nominative, genitive, dative, accusative, instrumental, locative, vocative
Number: singular, plural
Gender: masculine, feminine, neuter

Sentence: {text}"""

    try:
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0
        )
        analysis_results = chat.choices[0].message.content.strip().split('\n')
    except Exception as e:
        return f"Błąd AI: {e}", []

    final_result = []
    debug_logs = []

    for line in analysis_results:
        if "|" not in line: continue
        parts = [p.strip().lower() for p in line.split('|')]
        if len(parts) < 3: continue
        
        pl_word = re.sub(r'[^\w\s]', '', parts[0])
        case_tag, num_tag = parts[1], parts[2]

        # A. Szukanie rdzenia w osnova.json
        slov_root = None
        for entry in osnova_db:
            if entry.get('polish', '').lower() == pl_word:
                slov_root = entry.get('slovian')
                break
        
        # B. Mapowanie formy z vuzor.json (Rygorystyczne)
        if slov_root:
            best_match = None
            for pattern in vuzor_db:
                v_info = pattern.get("type and case", "").lower()
                v_form = pattern.get("slovian", "")
                
                # Warunek Hoenira: Rdzeń musi być identyczny, a tagi muszą się zgadzać
                if (f"'{slov_root}'" in v_info or slov_root == v_form) and \
                   case_tag in v_info and num_tag in v_info:
                    best_match = v_form
                    break
            
            if best_match:
                # Normalizacja końcowa (usuwanie polskich liter z wyniku)
                final_word = normalize_to_slovian(best_match)
                final_result.append(final_word)
                debug_logs.append(f"✅ {pl_word} -> {final_word} ({case_tag}, {num_tag})")
            else:
                # Jeśli brak w vuzor, wymuszamy normalizację rdzenia
                safe_root = normalize_to_slovian(slov_root)
                final_result.append(f"{safe_root}?")
                debug_logs.append(f"⚠️ Brak odmiany dla '{slov_root}'. Użyto rdzenia.")
        else:
            # Przyimki i słowa funkcyjne
            statics = {"w": "vu", "na": "na", "z": "iz", "i": "i", "siła": "sila"}
            replacement = statics.get(pl_word, normalize_to_slovian(pl_word))
            final_result.append(replacement)
            debug_logs.append(f"ℹ️ Słowo stałe/nieznane: {pl_word}")

    return " ".join(final_result).capitalize(), debug_logs

# ================== 5. INTERFEJS UŻYTKOWNIKA ==================

st.title("🏛️ Ekspercki Perkladačь (Hoenir Engine)")
st.markdown("### Precyzyjne mapowanie morfologiczne bez polskich liter")

input_sentence = st.text_input("Wpisz zdanie po polsku:", value="W Słowianach siła.")

if input_sentence:
    with st.spinner("Przetwarzanie przez silnik Hoenira..."):
        translated, logs = hoenir_engine(input_sentence)
        
        st.write("### Wynik tłumaczenia:")
        # Renderowanie wyniku w zielonej ramce, jak na Twoich screenach
        st.success(translated)
        
        with st.expander("Szczegóły mapowania (Logi silnika)"):
            for l in logs:
                st.write(l)

st.divider()
st.caption(f"Status: {len(osnova_db)} rdzeni | {len(vuzor_db)} form gramatycznych.")
