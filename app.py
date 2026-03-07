import streamlit as st
import json
import os
import re
from groq import Groq

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""<style>.main{background:#0e1117}.stTextArea textarea{background:#1a1a1a;color:#dcdcdc}</style>""", unsafe_allow_html=True)

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# ================== ŁADOWANIE BAZ ==================
@st.cache_data
def load_json(filename):
    if not os.path.exists(filename): return {}
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

osnova = load_json("osnova.json")
vuzor  = load_json("vuzor.json")   # <<< NOWOŚĆ

# ================== WZORY ODMIAN (z Twojego vuzor) ==================
DECLENSION_RULES = """
RZECZOWNIKI ŻEŃSKIE a-temat (obětьnica):
Sg: nom-a acc-ǫ gen/dat/loc-i ins-ejǫ voc-e
Pl: nom/acc/voc-i gen-∅ loc-ah dat-am ins-ami

ŻEŃSKIE i-temat (-ostь):
Sg: nom/acc/voc-ь gen/dat/loc-i ins-ьjǫ
Pl: nom/acc/voc-i gen-ьji loc-ih dat-im ins-ьmi

NIJAKIE o-temat (ljudovoldьstvo):
Sg: nom/acc/voc-o gen-a loc-ě dat-u ins-omь
Pl: nom/acc/voc-a gen-∅ loc-ěh dat-om ins-y

NIJAKIE je-temat (bytьje):
Sg: nom/acc/voc-ьje gen-ьja loc-ьji dat-ьju ins-ьjemь
Pl: nom/acc/voc-ьja gen-ьji loc-ьjih dat-ьjem ins-ьji

PRZYMIOTNIKI twarde (slověnьsky):
M sg: -y / -ogo / -omu / -ymь / -om
F sg: -a / -ǫ / -oje / -ojǫ
N sg: -e / -ogo / -omu / -ymь / -om
Pl M: -i / -yh / -ymь / -ymi
"""

# ================== LEPSZE WYSZUKIWANIE ==================
def get_context(text, dic):
    words = re.findall(r'\w+', text.lower())
    entries = []
    for w in words:
        if w in dic:
            entries.extend(dic[w])
        elif len(w) >= 4:
            prefix = w[:4]
            for base in dic:
                if base.startswith(prefix):
                    entries.extend(dic[base])
    # deduplikacja
    seen = {(e['polish'].lower(), e['slovian'].lower()) for e in entries}
    return [e for e in entries if (e['polish'].lower(), e['slovian'].lower()) in seen]

dictionary = {e.get("polish","").lower().strip(): [e] for e in osnova}

# ================== INTERFEJS ==================
st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši slovo alibo rěčenьje:", placeholder="Np. W miastach siła.", height=150)

if user_input:
    with st.spinner("Przetwarzanie..."):
        matches = get_context(user_input, dictionary)
        mapping = "\n".join([f"PL '{m['polish']}' → SL '{m['slovian']}'" for m in matches])

        system_prompt = f"""
Jesteś precyzyjnym tłumaczem na język słowiański (prasłowiański).
Używasz TYLKO słów z osnova.json + wzorów z vuzor.json.

WZORY ODMIAN (używaj ich ściśle):
{DECLENSION_RULES}

ALGORYTM:
1. Dla każdego polskiego słowa znajdź rdzeń w osnova.json
2. Określ przypadek/liczbę/rodzaj/żywotność
3. Zastosuj dokładnie wzór z sekcji powyżej
4. Jeśli nie ma wzoru → (ne najdeno slova)

DANE:
{mapping}

Zasady: szyk przymiotnik przed rzeczownikiem, zachowaj interpunkcję i wielkość liter. Bez komentarzy.
"""

        try:
            chat = client.chat.completions.create(
                model="openai/gpt-oss-120b",   # poprawiony model Groq
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Tekst: {user_input}"}
                ],
                temperature=0.0,
                max_tokens=1024
            )
            result = chat.choices[0].message.content.strip()
            st.markdown("### Vynik perklada:")
            st.success(result)
        except Exception as e:
            st.error(f"Błąd: {e}")

