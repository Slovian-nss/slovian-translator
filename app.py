import streamlit as st
import json
import os
import re
from groq import Groq

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea > div > div > textarea { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KONFIGURACJA GROQ
# ============================================================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# 3. ŁADOWANIE BAZ
# ============================================================
@st.cache_data
def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

osnova = load_json("osnova.json")
vuzor  = load_json("vuzor.json")  # wczytujemy, ale używamy wzorów w prompcie

# Budowa słownika po polsku (klucz = forma podstawowa lowercase)
dictionary = {}
for entry in osnova:
    pl = entry.get("polish", "").lower().strip()
    if pl:
        if pl not in dictionary:
            dictionary[pl] = []
        dictionary[pl].append(entry)

# ============================================================
# 4. WZORY ODMIAN + SPECJALNA REGUŁA DLA "GORD"
# ============================================================
DECLENSION_RULES = """
RZECZOWNIKI MĘSKIE o-temat twardy (gord / obgord):
Sg: nom gord, acc gord, gen gorda, loc gordě, dat gordu, ins gordomь, voc gorde
Pl: nom gorde, acc gordy, gen gord, loc gorděh, dat gordom, ins gordy

RZECZOWNIKI ŻEŃSKIE a-temat (obětьnica):
Sg: nom-a acc-ǫ gen/dat/loc-i ins-ejǫ voc-e
Pl: nom/acc/voc-i gen-∅ loc-ah dat-am ins-ami

ŻEŃSKIE i-temat (-ostь):
Sg: nom/acc/voc-ь gen/dat/loc-i ins-ьjǫ
Pl: nom/acc/voc-i gen-ьji loc-ih dat-im ins-ьmi

NIJAKIE o-temat (ljudovoldьstvo):
Sg: nom/acc/voc-o gen-a loc-ě dat-u ins-omь
Pl: nom/acc/voc-a gen-∅ loc-ěh dat-om ins-y

PRZYMIOTNIKI twarde (slověnьsky):
M sg: -y / -ogo / -omu / -ymь
F sg: -a / -ǫ / -oje / -ojǫ
N sg: -e / -ogo / -omu / -ymь
"""

# ============================================================
# 5. LEPSZE WYSZUKIWANIE (z obsługą "miasto" → "gord")
# ============================================================
def get_context(text, dic):
    words = re.findall(r'\w+', text.lower())
    entries = []
    polish_endings = ['ie','u','em','ach','om','ami','ów','a','y','i','ego','emu','ej','ą','e']
    for w in words:
        if w in dic:
            entries.extend(dic[w])
            continue
        for end in polish_endings:
            if w.endswith(end) and len(w) > len(end)+2:
                stem = w[:-len(end)]
                if stem in dic:
                    entries.extend(dic[stem])
                    break
        # SPECJALNA REGUŁA: "miasto" / "mieście" / "miastach" → gord
        if 'miast' in w and 'miasto' in dic:
            entries.extend(dic['miasto'])
    seen = {(e['polish'].lower(), e['slovian'].lower()) for e in entries}
    return [e for e in entries if (e['polish'].lower(), e['slovian'].lower()) in seen]

# ============================================================
# 6. INTERFEJS
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši slovo alibo rěčenьje:", placeholder="Np. W mieście.", height=150)

if user_input:
    with st.spinner("Przetwarzanie..."):
        matches = get_context(user_input, dictionary)
        mapping = "\n".join([f"PL '{m['polish']}' → SL '{m['slovian']}'" for m in matches])

        system_prompt = f"""
Jesteś precyzyjnym tłumaczem na prasłowiański (slověnьsky).
Używaj TYLKO słów z osnova.json i wzorów z vuzor.json.

WZORY ODMIAN (używaj ściśle):
{DECLENSION_RULES}

Deklinacja "gord" (miasto) i "obgord" (ogród) – męski o-temat twardy:
Sg loc: gordě
Przykład: "W mieście" = "vu gordě".

ALGORYTM:
1. Dla każdego polskiego słowa znajdź rdzeń w osnova.json
2. Określ przypadek/liczbę/rodzaj/żywotność
3. Zastosuj dokładnie wzór powyżej
4. Jeśli brak → (ne najdeno slova)

DANE MAPOWANIA:
{mapping}

Zasady: przymiotnik przed rzeczownikiem, zachowaj interpunkcję i wielkość liter. Bez komentarzy.
"""

        try:
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"TEKST DO KONWERSJI: {user_input}"}
                ],
                temperature=0.0,
                max_tokens=1024
            )
            result = chat_completion.choices[0].message.content.strip()
            st.markdown("### Vynik perklada:")
            st.success(result)
        except Exception as e:
            st.error(f"Błąd modelu: {e}")

        if matches:
            with st.expander("Użyte mapowanie z bazy"):
                for m in matches:
                    st.write(f"'{m['polish']}' → `{m['slovian']}`")
