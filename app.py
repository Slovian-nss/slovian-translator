import streamlit as st
import json
import os
import re

# ============================================================
# 1. ŁADOWANIE DANYCH (Zabezpieczone)
# ============================================================
@st.cache_data
def load_all_data():
    osnova, vuzor = [], {}
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    if os.path.exists("vuzor.json"):
        with open("vuzor.json", "r", encoding="utf-8") as f:
            vuzor = json.load(f)
    return osnova, vuzor

osnova, vuzor = load_all_data()

# ============================================================
# 2. SILNIK LINGWISTYCZNY (Logika odporna na błędy)
# ============================================================

def get_clean_stem(slovian_word):
    """Usuwa jery końcowe, aby przygotować rdzeń pod nową końcówkę."""
    return slovian_word.rstrip('ъь')

def translate_word(polish_word, target_case="nominative"):
    pw = polish_word.lower().strip(",.?! ")
    
    # 1. Szukanie w osnova.json
    entry = next((e for e in osnova if e['polish'].lower() == pw), None)
    
    # Próba lematyzacji (jeśli wpisano 'ogrodzie', szukaj czegoś co zaczyna się na 'ogrod')
    if not entry:
        entry = next((e for e in osnova if pw.startswith(e['polish'].lower()[:4])), None)

    if not entry:
        return f"({polish_word}?)"

    # 2. Pobieranie danych o słowie
    slovian_nom = entry.get('slovian', '')
    category = entry.get('type and case', '')
    
    # 3. Pobieranie końcówki z vuzor.json
    # vuzor[category] zwraca słownik przypadków, np. {"nominative": "ъ", "locative": "ě"}
    suffix = ""
    if category in vuzor:
        suffix = vuzor[category].get(target_case, vuzor[category].get("nominative", ""))
    
    # 4. Budowanie słowa
    stem = get_clean_stem(slovian_nom)
    final_word = stem + suffix
    
    # 5. Reguły palatalizacji (Valhyr style)
    # Jeśli końcówka to 'ě', a rdzeń kończy się na g/k/h
    if suffix.startswith('ě'):
        if stem.endswith('g'): final_word = stem[:-1] + "dz" + suffix
        elif stem.endswith('k'): final_word = stem[:-1] + "c" + suffix
        elif stem.endswith('h'): final_word = stem[:-1] + "z" + suffix

    return final_word

def run_translator(text):
    if not text: return ""
    
    # Rozbijanie na słowa z zachowaniem znaków interpunkcyjnych
    tokens = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    result = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        low_token = token.lower()
        
        # Obsługa przyimków
        if low_token in ["w", "v", "we"]:
            result.append("vu")
            i += 1
            if i < len(tokens):
                # Następne słowo w miejscowniku
                result.append(translate_word(tokens[i], "locative"))
        elif low_token == "jestem":
            result.append("esmb")
        elif re.match(r'\w+', token):
            result.append(translate_word(token, "nominative"))
        else:
            result.append(token) # Interpunkcja
        i += 1
        
    return " ".join(result).replace(" .", ".").replace(" ,", ",")

# ============================================================
# 3. INTERFEJS STREAMLIT
# ============================================================
st.title("Perkladačь (Valhyr Engine V4)")

if not osnova or not vuzor:
    st.error("⚠️ Nie znaleziono plików bazy danych! Upewnij się, że osnova.json i vuzor.json są w tym samym folderze.")
else:
    user_input = st.text_input("Wpisz zdanie po polsku:", value="Jestem w ogrodzie")

    if user_input:
        try:
            output = run_translator(user_input)
            st.markdown("### Vynik perklada:")
            st.success(output)
        except Exception as e:
            st.error(f"Wystąpił błąd podczas tłumaczenia: {e}")

    # Podgląd bazy dla pewności
    with st.expander("Podgląd bazy (Debug)"):
        col1, col2 = st.columns(2)
        col1.write("Liczba słów w osnova:")
        col1.write(len(osnova))
        col2.write("Liczba wzorców w vuzor:")
        col2.write(len(vuzor))
