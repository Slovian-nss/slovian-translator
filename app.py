import streamlit as st
import json
import os
import re

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь (Local Engine)", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.5rem; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. LOKALNY SILNIK LINGWISTYCZNY (Logika Valhyr)
# ============================================================

@st.cache_data
def load_data():
    # Ładowanie osnova.json (Słownik)
    osnova = {}
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for entry in data:
                pl = entry.get("polish", "").lower().strip()
                if pl not in osnova: osnova[pl] = []
                osnova[pl].append(entry)
    
    # Ładowanie vuzor.json (Wzorce odmian)
    vuzory = {}
    if os.path.exists("vuzor.json"):
        with open("vuzor.json", "r", encoding="utf-8") as f:
            vuzory = json.load(f)
            
    return osnova, vuzory

osnova, vuzory = load_data()

def match_case(original, translated):
    """Przenosi wielkość liter z oryginału na tłumaczenie."""
    if original.isupper(): return translated.upper()
    if original[0].isupper(): return translated.capitalize()
    return translated.lower()

def apply_grammar_rules(word, pos_type, context):
    """
    Tu działają reguły Valhyr: np. palatalizacja g -> dz przed 'ě'
    """
    # Przykład palatalizacji: rěka -> rěcě, sluga -> sludzě
    if context == "locative":
        if word.endswith("ga"): return word[:-2] + "dzě"
        if word.endswith("ka"): return word[:-2] + "cě"
    return word

def translate_local(text):
    """Główny silnik tłumaczący bez użycia AI."""
    words = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    translated_sentence = []
    
    # Tymczasowy bufor dla przymiotników (aby zmienić szyk)
    adj_buffer = None

    for word in words:
        low_word = word.lower()
        
        # Jeśli to nie słowo (tylko znak interpunkcyjny)
        if not re.match(r'\w+', word):
            translated_sentence.append(word)
            continue

        # Szukanie w osnova.json
        entry = osnova.get(low_word)
        
        if entry:
            # Wybieramy pierwsze dopasowanie (w pełnej wersji tutaj byłaby logika kontekstu)
            best_match = entry[0]
            slovian_word = best_match['slovian']
            pos = best_match.get('type and case', '').lower()
            
            # Logika odmian i palatalizacji
            slovian_word = apply_grammar_rules(slovian_word, pos, "locative" if "miejscownik" in low_word else "norm")
            
            final_word = match_case(word, slovian_word)
            
            # Logika szyku: Przymiotnik przed rzeczownik
            if "adjective" in pos or "pridavьnik" in pos:
                adj_buffer = final_word
            else:
                if adj_buffer:
                    translated_sentence.append(adj_buffer)
                    adj_buffer = None
                translated_sentence.append(final_word)
        else:
            # Brak słowa
            translated_sentence.append(f"({match_case(word, 'ne najdeno slova')})")

    if adj_buffer: # Jeśli przymiotnik został na końcu
        translated_sentence.append(adj_buffer)

    # Łączenie w zdanie z poprawką na interpunkcję
    return "".join([" " + i if not re.match(r'[^\w\s]', i) else i for i in translated_sentence]).strip()

# ============================================================
# 3. INTERFEJS UŻYTKOWNIKA
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")
st.caption("Lokalny silnik lingwistyczny (Valhyr-style) • Offline")

user_input = st.text_input("Vupiši slovo abo rěčenьje:", placeholder="np. Wojsko Słowiańskie")

if user_input:
    # Tłumaczenie odbywa się natychmiastowo na procesorze użytkownika
    result = translate_local(user_input)
    
    st.markdown("### Vynik perklada:")
    st.success(result)
    
    st.info("ℹ️ Tłumaczenie wygenerowane lokalnie przez reguły gramatyczne, bez udziału zewnętrznych serwerów AI.")
