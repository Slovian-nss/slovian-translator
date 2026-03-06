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
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stTextArea > div > div > textarea { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KONFIGURACJA KLIENTA GROQ
# ============================================================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# 3. ŁADOWANIE BAZY DANYCH
# ============================================================
@st.cache_data
def load_dictionary():
    if not os.path.exists("osnova.json"):
        return {}
    try:
        with open("osnova.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        index = {}
        for entry in data:
            pl = entry.get("polish", "").lower().strip()
            if pl:
                if pl not in index: index[pl] = []
                index[pl].append(entry)
        return index
    except Exception as e:
        st.error(f"Błąd bazy: {e}")
        return {}

dictionary = load_dictionary()

# ============================================================
# 4. PRECYZYJNA LOGIKA POBIERANIA KONTEKSTU (Słowa + Frazy)
# ============================================================
def get_strict_context(text, dic):
    # Wyciągamy słowa, ignorując interpunkcję dla wyszukiwania
    search_text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = search_text.split()
    relevant_entries = []
    
    for word in words:
        if word in dic:
            relevant_entries.extend(dic[word])
    
    seen = set()
    unique_entries = []
    for e in relevant_entries:
        identifier = (e['polish'].lower(), e['slovian'].lower())
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(e)
            
    return unique_entries

# ============================================================
# 5. INTERFEJS UŻYTKOWNIKA
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

# Używamy text_area zamiast text_input dla obsługi wielu linii
user_input = st.text_area("Vupiši slovo alibo rěčenьje:", placeholder="", height=200)

if user_input:
    with st.spinner("Przetwarzanie tekstu..."):
        matches = get_strict_context(user_input, dictionary)
        
        # Przygotowanie bardzo technicznej instrukcji mapowania
        mapping_rules = "\n".join([
            f"MAPUJ: '{m['polish']}' NA '{m['slovian']}'"
            for m in matches
        ])

        system_prompt = """
Jesteś deterministycznym parserem i generatorem fleksji
rekonstruowanego języka słowiańskiego.

Twoim jedynym zadaniem jest zamiana polskich form słów
na ich słowiańskie odpowiedniki fleksyjne
na podstawie danych z:

- osnova.json
- vuzor.json

Nie jesteś tłumaczem.
Nie interpretujesz znaczeń.
Nie tworzysz nowych form.

--------------------------------------------------
ZASADA GŁÓWNA
--------------------------------------------------

Forma słowa powstaje według schematu:

RDZEŃ (osnova.json) + KOŃCÓWKA (vuzor.json)

Końcówki z vuzor.json są jedynym źródłem fleksji.

--------------------------------------------------
STRUKTURA DANYCH
--------------------------------------------------

osnova.json

{
  "polskie_slowo": {
      "rdzen": "slowianski_rdzen",
      "vuzor": "nazwa_wzoru",
      "pos": "noun | adjective | adverb"
  }
}

--------------------------------------------------

vuzor.json

type and case	context	polish	slovian
noun - jimenьnik: "obětьnica" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promise	obietnica	obětьnica
noun - jimenьnik: "obětьnica" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promise	obietnicę	obětьnicǫ
noun - jimenьnik: "obětьnica" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promise	obietnicy	obětьnici
noun - jimenьnik: "obětьnica" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promise	obietnicy	obětьnici
noun - jimenьnik: "obětьnica" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promise	obietnicy	obětьnici
noun - jimenьnik: "obětьnica" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promise	obietnicą	obětьnicejǫ
noun - jimenьnik: "obětьnica" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promise	obietnico	obětьnice
noun - jimenьnik: "obětьnica" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promises	obietnice	obětьnici
noun - jimenьnik: "obětьnica" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promises	obietnice	obětьnici
noun - jimenьnik: "obětьnica" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promises	obietnic	obětьnic
noun - jimenьnik: "obětьnica" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promises	obietnicach	obětьnicah
noun - jimenьnik: "obětьnica" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promises	obietnicom	obětьnicam
noun - jimenьnik: "obětьnica" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promises	obietnicami	obětьnicami
noun - jimenьnik: "obětьnica" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	promises	obietnice	obětьnici
noun - jimenьnik: "okolica" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinity, neighbourhood	okolica	okolica
noun - jimenьnik: "okolica" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinity, neighbourhood	okolicę	okolicǫ
noun - jimenьnik: "okolica" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinity, neighbourhood	okolicy	okolici
noun - jimenьnik: "okolica" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinity, neighbourhood	okolicy	okolici
noun - jimenьnik: "okolica" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinity, neighbourhood	okolicy	okolici
noun - jimenьnik: "okolica" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinity, neighbourhood	okolicą	okolicejǫ
noun - jimenьnik: "okolica" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinity, neighbourhood	okolico	okolice
noun - jimenьnik: "okolica" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinities, neighbourhoods	okolice	okolici
noun - jimenьnik: "okolica" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinities, neighbourhoods	okolice	okolici
noun - jimenьnik: "okolica" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinities, neighbourhoods	okolic	okolic
noun - jimenьnik: "okolica" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinities, neighbourhoods	okolicach	okolicah
noun - jimenьnik: "okolica" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinities, neighbourhoods	okolicom	okolicam
noun - jimenьnik: "okolica" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinities, neighbourhoods	okolicami	okolicami
noun - jimenьnik: "okolica" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	surroundings, vicinities, neighbourhoods	okolice	okolici
noun - jimenьnik: "božьnica" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	church, temple	bożnica	božьnica
noun - jimenьnik: "božьnica" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	church, temple	bożnicę	božьnicǫ
noun - jimenьnik: "božьnica" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	church, temple	bożnicy	božьnici
noun - jimenьnik: "božьnica" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	church, temple	bożnicy	božьnici
noun - jimenьnik: "božьnica" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	church, temple	bożnicy	božьnici
noun - jimenьnik: "božьnica" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	church, temple	bożnicą	božьnicejǫ
noun - jimenьnik: "božьnica" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	church, temple	bożnico	božьnice
noun - jimenьnik: "božьnica" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	churches, temples	bożnice	božьnici
noun - jimenьnik: "božьnica" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	churches, temples	bożnice	božьnici
noun - jimenьnik: "božьnica" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	churches, temples	bożnic	božьnic
noun - jimenьnik: "božьnica" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	churches, temples	bożnicach	božьnicah
noun - jimenьnik: "božьnica" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	churches, temples	bożnicom	božьnicam
noun - jimenьnik: "božьnica" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	churches, temples	bożnicami	božьnicami
noun - jimenьnik: "božьnica" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	churches, temples	bożnice	božьnici
noun - jimenьnik: "usluga" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	service	usługa	usluga
noun - jimenьnik: "usluga" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	service	usługę	uslugǫ
noun - jimenьnik: "usluga" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	service	usługi	uslugy
noun - jimenьnik: "usluga" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	service	usłudze	usludzě
noun - jimenьnik: "usluga" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	service	usłudze	usludzě
noun - jimenьnik: "usluga" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	service	usługą	uslugojǫ
noun - jimenьnik: "usluga" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	service	usługo	uslugo
noun - jimenьnik: "usluga" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	services	usługi	uslugy
noun - jimenьnik: "usluga" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	services	usługi	uslugy
noun - jimenьnik: "usluga" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	services	usług	uslug
noun - jimenьnik: "usluga" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	services	usługach	uslugah
noun - jimenьnik: "usluga" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	services	usługom	uslugam
noun - jimenьnik: "usluga" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	services	usługami	uslugami
noun - jimenьnik: "usluga" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	services	usługi	uslugy
noun - jimenьnik: "mǫdrostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdom	mądrość	mǫdrostь
noun - jimenьnik: "mǫdrostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdom	mądrość	mǫdrostь
noun - jimenьnik: "mǫdrostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdom	mądrości	mǫdrosti
noun - jimenьnik: "mǫdrostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdom	mądrości	mǫdrosti
noun - jimenьnik: "mǫdrostь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdom	mądrości	mǫdrosti
noun - jimenьnik: "mǫdrostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdom	mądrością	mǫdrostьjǫ
noun - jimenьnik: "mǫdrostь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdom	mądrości	mǫdrostь
noun - jimenьnik: "mǫdrostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdoms	mądrości	mǫdrosti
noun - jimenьnik: "mǫdrostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdoms	mądrości	mǫdrosti
noun - jimenьnik: "mǫdrostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdoms	mądrości	mǫdrostьji
noun - jimenьnik: "mǫdrostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdoms	mądrościach	mǫdrostih
noun - jimenьnik: "mǫdrostь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdoms	mądrościom	mǫdrostim
noun - jimenьnik: "mǫdrostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdoms	mądrościami	mǫdrostьmi
noun - jimenьnik: "mǫdrostь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	wisdoms	mądrości	mǫdrostь
noun - jimenьnik: "hytrostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunning, slyness, craftiness	chytrość	chytrostь
noun - jimenьnik: "hytrostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunning, slyness, craftiness	chytrość	chytrostь
noun - jimenьnik: "hytrostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunning, slyness, craftiness	chytrości	chytrosti
noun - jimenьnik: "hytrostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunning, slyness, craftiness	chytrości	chytrosti
noun - jimenьnik: "hytrostь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunning, slyness, craftiness	chytrości	chytrosti
noun - jimenьnik: "hytrostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunning, slyness, craftiness	chytrością	chytrostьjǫ
noun - jimenьnik: "hytrostь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunning, slyness, craftiness	chytrości	chytrostь
noun - jimenьnik: "hytrostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunnings, slynesses, craftinesses	chytrości	chytrosti
noun - jimenьnik: "hytrostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunnings, slynesses, craftinesses	chytrości	chytrosti
noun - jimenьnik: "hytrostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunnings, slynesses, craftinesses	chytrości	chytrostьji
noun - jimenьnik: "hytrostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunnings, slynesses, craftinesses	chytrościach	chytrostih
noun - jimenьnik: "hytrostь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunnings, slynesses, craftinesses	chytrościom	chytrostim
noun - jimenьnik: "hytrostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunnings, slynesses, craftinesses	chytrościami	chytrostьmi
noun - jimenьnik: "hytrostь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cunnings, slynesses, craftinesses	chytrości	chytrosti
noun - jimenьnik: "dobrotь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindness	dobroć	dobrotь
noun - jimenьnik: "dobrotь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindness	dobroć	dobrotь
noun - jimenьnik: "dobrotь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindness	dobroci	dobroti
noun - jimenьnik: "dobrotь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindness	dobroci	dobroti
noun - jimenьnik: "dobrotь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindness	dobroci	dobroti
noun - jimenьnik: "dobrotь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindness	dobrocią	dobrotьjǫ
noun - jimenьnik: "dobrotь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindness	dobroci	dobrotь
noun - jimenьnik: "dobrotь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindnesses	dobroci	dobroti
noun - jimenьnik: "dobrotь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindnesses	dobroci	dobroti
noun - jimenьnik: "dobrotь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindnesses	dobroci	dobrotьji
noun - jimenьnik: "dobrotь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindnesses	dobrociach	dobrotih
noun - jimenьnik: "dobrotь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindnesses	dobrociom	dobrotim
noun - jimenьnik: "dobrotь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindnesses	dobrociami	dobrotьmi
noun - jimenьnik: "dobrotь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	kindnesses	dobroci	dobrotь
noun - jimenьnik: "prodadja" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sale	sprzedaż	prodadja
noun - jimenьnik: "prodadja" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sale	sprzedaż	prodadjǫ
noun - jimenьnik: "prodadja" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sale	sprzedaży	prodadji
noun - jimenьnik: "prodadja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sale	sprzedaży	prodadji
noun - jimenьnik: "prodadja" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sale	sprzedaży	prodadji
noun - jimenьnik: "prodadja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sale	sprzedażą	prodadjejǫ
noun - jimenьnik: "prodadja" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sale	sprzedaży	prodadjo
noun - jimenьnik: "prodadja" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sales	sprzedaże	prodadji
noun - jimenьnik: "prodadja" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sales	sprzedaże	prodadji
noun - jimenьnik: "prodadja" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sales	sprzedaży	prodadj
noun - jimenьnik: "prodadja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sales	sprzedażach	prodadjah
noun - jimenьnik: "prodadja" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sales	sprzedażom	prodadjam
noun - jimenьnik: "prodadja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sales	sprzedażami	prodadjami
noun - jimenьnik: "prodadja" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sales	sprzedaże	prodadji
noun - jimenьnik: "bytьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	being	bycie	bytьje
noun - jimenьnik: "bytьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	being	bycie	bytьje
noun - jimenьnik: "bytьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	being	bycia	bytьja
noun - jimenьnik: "bytьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	being	byciu	bytьji
noun - jimenьnik: "bytьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	being	byciu	bytьju
noun - jimenьnik: "bytьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	being	byciem	bytьjemь
noun - jimenьnik: "bytьje" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	being	bycie	bytьje
noun - jimenьnik: "bytьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	beings	bycia	bytьja
noun - jimenьnik: "bytьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	beings	bycia	bytьja
noun - jimenьnik: "bytьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	beings	być	bytьji
noun - jimenьnik: "bytьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	beings	byciach	bytьjih
noun - jimenьnik: "bytьje" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	beings	byciom	bytьjem
noun - jimenьnik: "bytьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	beings	byciami	bytьji
noun - jimenьnik: "bytьje" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	beings	bycia	bytьja
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowładztwo	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowładztwo	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowładztwa	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowładztwie	ljudovoldьstvě
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowładztwu	ljudovoldьstvu
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowładztwem	ljudovoldьstvomь
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowładztwo	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowładztwa	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowładztwa	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowładztw	ljudovoldьstv
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowładztwach	ljudovoldьstvěh
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowładztwom	ljudovoldьstvom
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowładztwami	ljudovoldьstvy
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowładztwa	ljudovoldьstva
noun - jimenьnik: "pohota" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greed	chciwość	pohota
noun - jimenьnik: "pohota" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greed	chciwość	pohotǫ
noun - jimenьnik: "pohota" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greed	chciwości	pohoty
noun - jimenьnik: "pohota" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greed	chciwości	pohotě
noun - jimenьnik: "pohota" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greed	chciwością	pohotojǫ
noun - jimenьnik: "pohota" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greed	chciwości	pohotě
noun - jimenьnik: "pohota" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greed	chciwości	pohoto
noun - jimenьnik: "pohota" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greeds	chciwości	pohoty
noun - jimenьnik: "pohota" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greeds	chciwości	pohoty
noun - jimenьnik: "pohota" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greeds	chciwości	pohot
noun - jimenьnik: "pohota" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greeds	chciwościom	pohotam
noun - jimenьnik: "pohota" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greeds	chciwościami	pohotami
noun - jimenьnik: "pohota" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greeds	chciwościach	pohotah
noun - jimenьnik: "pohota" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greeds	chciwości	pohoty
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracy	demokracja	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracy	demokracja	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracy	demokracji	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracy	demokracji	ljudovoldьstvu
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracy	demokracją	ljudovoldьstvomь
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracy	demokracji	ljudovoldьstvě
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracy	demokracjo	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracies	demokracje	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracies	demokracje	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracies	demokracji	ljudovoldьstv
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracies	demokracjom	ljudovoldьstvom
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracies	demokracjami	ljudovoldьstvy
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracies	demokracjach	ljudovoldьstvěh
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	democracies	demokracje	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowłodztwo	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowłodztwo	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowłodztwa	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowłodztwu	ljudovoldьstvu
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowłodztwem	ljudovoldьstvomь
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowłodztwie	ljudovoldьstvě
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rule	ludowłodztwo	ljudovoldьstvo
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowłodztwa	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowłodztwa	ljudovoldьstva
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowłodztw	ljudovoldьstv
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowłodztwom	ljudovoldьstvom
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowłodztwami	ljudovoldьstvy
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowłodztwach	ljudovoldьstvěh
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	people's rules	ludowłodztwa	ljudovoldьstva
noun - jimenьnik: "pohota" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greediness	pazerność	pohota
noun - jimenьnik: "pohota" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greediness	pazerność	pohotǫ
noun - jimenьnik: "pohota" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greediness	pazerności	pohoty
noun - jimenьnik: "pohota" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greediness	pazerności	pohotě
noun - jimenьnik: "pohota" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greediness	pazerności	pohotě
noun - jimenьnik: "pohota" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greediness	pazernością	pohotojǫ
noun - jimenьnik: "pohota" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greediness	pazerności	pohoto
noun - jimenьnik: "pohota" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greedinesses	pazerności	pohoty
noun - jimenьnik: "pohota" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greedinesses	pazerności	pohoty
noun - jimenьnik: "pohota" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greedinesses	pazerności	pohot
noun - jimenьnik: "pohota" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greedinesses	pazernościach	pohotah
noun - jimenьnik: "pohota" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greedinesses	pazernościom	pohotam
noun - jimenьnik: "pohota" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greedinesses	pazernościami	pohotami
noun - jimenьnik: "pohota" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	greedinesses	pazerności	pohoty
noun - jimenьnik: "samotьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	loneliness	samotność	samotьnostь
noun - jimenьnik: "samotьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	loneliness	samotność	samotьnostь
noun - jimenьnik: "samotьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	loneliness	samotności	samotьnosti
noun - jimenьnik: "samotьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	loneliness	samotności	samotьnosti
noun - jimenьnik: "samotьnostь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	loneliness	samotności	samotьnosti
noun - jimenьnik: "samotьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	loneliness	samotnością	samotьnostьjǫ
noun - jimenьnik: "samotьnostь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	loneliness	samotności	samotьnosti
noun - jimenьnik: "samotьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lonelinesses	samotności	samotьnosti
noun - jimenьnik: "samotьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lonelinesses	samotności	samotьnosti
noun - jimenьnik: "samotьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lonelinesses	samotności	samotьnosti
noun - jimenьnik: "samotьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lonelinesses	samotnościach	samotьnostih
noun - jimenьnik: "samotьnostь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lonelinesses	samotnościom	samotьnostim
noun - jimenьnik: "samotьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lonelinesses	samotnościami	samotьnostьmi
noun - jimenьnik: "samotьnostь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lonelinesses	samotności	samotьnosti
noun - jimenьnik: "hotěnьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wanting	chcenie	hotěnьje
noun - jimenьnik: "hotěnьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wanting	chcenie	hotěnьje
noun - jimenьnik: "hotěnьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wanting	chcenia	hotěnьja
noun - jimenьnik: "hotěnьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wanting	chceniu	hotěnьji
noun - jimenьnik: "hotěnьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wanting	chceniu	hotěnьju
noun - jimenьnik: "hotěnьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wanting	chceniem	hotěnьjemь
noun - jimenьnik: "hotěnьje" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wanting	chcenie	hotěnьje
noun - jimenьnik: "hotěnьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wantings	chcenia	hotěnьja
noun - jimenьnik: "hotěnьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wantings	chcenia	hotěnьja
noun - jimenьnik: "hotěnьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wantings	chceń	hotěnij
noun - jimenьnik: "hotěnьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wantings	chceniach	hotěnьjih
noun - jimenьnik: "hotěnьje" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wantings	chceniom	hotěnьjem
noun - jimenьnik: "hotěnьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wantings	chceniami	hotěnьji
noun - jimenьnik: "hotěnьje" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	wantings	chcenia	hotěnьja
noun - jimenьnik: "nehotěnьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingness	niechcenie	nehotěnьje
noun - jimenьnik: "nehotěnьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingness	niechcenie	nehotěnьje
noun - jimenьnik: "nehotěnьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingness	niechcenia	nehotěnьja
noun - jimenьnik: "nehotěnьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingness	niechceniu	nehotěnьji
noun - jimenьnik: "nehotěnьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingness	niechceniu	nehotěnьju
noun - jimenьnik: "nehotěnьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingness	niechceniem	nehotěnьjemь
noun - jimenьnik: "nehotěnьje" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingness	niechcenie	nehotěnьje
noun - jimenьnik: "nehotěnьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingnesses	niechcenia	nehotěnьja
noun - jimenьnik: "nehotěnьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingnesses	niechcenia	nehotěnьja
noun - jimenьnik: "nehotěnьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingnesses	niechceń	nehotěnij
noun - jimenьnik: "nehotěnьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingnesses	niechceniach	nehotěnьjih
noun - jimenьnik: "nehotěnьje" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingnesses	niechceniom	nehotěnьjem
noun - jimenьnik: "nehotěnьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingnesses	niechceniami	nehotěnьji
noun - jimenьnik: "nehotěnьje" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	unwillingnesses	niechcenia	nehotěnьja
noun - jimenьnik: "orzkošь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delight	rozkosz	orzkošь
noun - jimenьnik: "orzkošь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delight	rozkosz	orzkošь
noun - jimenьnik: "orzkošь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delight	rozkoszy	orzkoši
noun - jimenьnik: "orzkošь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delight	rozkoszy	orzkoši
noun - jimenьnik: "orzkošь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delight	rozkoszy	orzkoši
noun - jimenьnik: "orzkošь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delight	rozkoszą	orzkošьjǫ
noun - jimenьnik: "orzkošь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delight	rozkoszy	orzkoši
noun - jimenьnik: "orzkošь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delights	rozkosze	orzkoši
noun - jimenьnik: "orzkošь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delights	rozkosze	orzkoši
noun - jimenьnik: "orzkošь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delights	rozkoszy	orzkoši
noun - jimenьnik: "orzkošь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delights	rozkoszach	orzkoših
noun - jimenьnik: "orzkošь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delights	rozkoszom	orzkošim
noun - jimenьnik: "orzkošь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delights	rozkoszami	orzkošьmi
noun - jimenьnik: "orzkošь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	delights	rozkosze	orzkoši
noun - jimenьnik: "orzkošь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxury	luksus	orzkošь
noun - jimenьnik: "orzkošь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxury	luksus	orzkošь
noun - jimenьnik: "orzkošь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxury	luksusu	orzkoši
noun - jimenьnik: "orzkošь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxury	luksusie	orzkoši
noun - jimenьnik: "orzkošь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxury	luksusowi	orzkoši
noun - jimenьnik: "orzkošь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxury	luksusem	orzkošьjǫ
noun - jimenьnik: "orzkošь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxury	luksusie	orzkoši
noun - jimenьnik: "orzkošь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxuries	luksusy	orzkoši
noun - jimenьnik: "orzkošь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxuries	luksusy	orzkoši
noun - jimenьnik: "orzkošь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxuries	luksusów	orzkoši
noun - jimenьnik: "orzkošь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxuries	luksusach	orzkoših
noun - jimenьnik: "orzkošь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxuries	luksusom	orzkošim
noun - jimenьnik: "orzkošь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxuries	luksusami	orzkošьmi
noun - jimenьnik: "orzkošь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	luxuries	luksusy	orzkoši
noun - jimenьnik: "jimenovanьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nomination	mianowanie	jimenovanьje
noun - jimenьnik: "jimenovanьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nomination	mianowanie	jimenovanьje
noun - jimenьnik: "jimenovanьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nomination	mianowania	jimenovanьja
noun - jimenьnik: "jimenovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nomination	mianowaniu	jimenovanьji
noun - jimenьnik: "jimenovanьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nomination	mianowaniu	jimenovanьju
noun - jimenьnik: "jimenovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nomination	mianowaniem	jimenovanьjemь
noun - jimenьnik: "jimenovanьje" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nomination	mianowanie	jimenovanьje
noun - jimenьnik: "jimenovanьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nominations	mianowania	jimenovanьja
noun - jimenьnik: "jimenovanьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nominations	mianowania	jimenovanьja
noun - jimenьnik: "jimenovanьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nominations	mianowań	jimenovanij
noun - jimenьnik: "jimenovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nominations	mianowaniach	jimenovanьjih
noun - jimenьnik: "jimenovanьje" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nominations	mianowaniom	jimenovanьjem
noun - jimenьnik: "jimenovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nominations	mianowaniami	jimenovanьji
noun - jimenьnik: "jimenovanьje" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	nominations	mianowania	jimenovanьja
noun - jimenьnik: "jimenovanьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	imianowanie	jimenovanьje
noun - jimenьnik: "jimenovanьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	imianowanie	jimenovanьje
noun - jimenьnik: "jimenovanьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	imianowania	jimenovanьja
noun - jimenьnik: "jimenovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	imianowaniu	jimenovanьji
noun - jimenьnik: "jimenovanьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	imianowaniu	jimenovanьju
noun - jimenьnik: "jimenovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	imianowaniem	jimenovanьjemь
noun - jimenьnik: "jimenovanьje" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	imianowanie	jimenovanьje
noun - jimenьnik: "jimenovanьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	imianowania	jimenovanьja
noun - jimenьnik: "jimenovanьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	imianowania	jimenovanьja
noun - jimenьnik: "jimenovanьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	imianowań	jimenovanij
noun - jimenьnik: "jimenovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	imianowaniach	jimenovanьjih
noun - jimenьnik: "jimenovanьje" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	imianowaniom	jimenovanьjem
noun - jimenьnik: "jimenovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	imianowaniami	jimenovanьji
noun - jimenьnik: "jimenovanьje" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	imianowania	jimenovanьja
noun - jimenьnik: "jimę" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	imię	jimę
noun - jimenьnik: "jimę" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	imię	jimę
noun - jimenьnik: "jimę" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	imienia	jimena
noun - jimenьnik: "jimę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	imieniu	jimene
noun - jimenьnik: "jimę" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	imieniu	jimeni
noun - jimenьnik: "jimę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	imieniem	jimenimь
noun - jimenьnik: "jimę" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	imię	jimę
noun - jimenьnik: "jimę" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	imiona	jimena
noun - jimenьnik: "jimę" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	imiona	jimena
noun - jimenьnik: "jimę" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	imion	jimen
noun - jimenьnik: "jimę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	imionach	jimenih
noun - jimenьnik: "jimę" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	imionom	jimenim
noun - jimenьnik: "jimę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	imionami	jimeny
noun - jimenьnik: "jimę" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	imiona	jimena
noun - jimenьnik: "vermę" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	wrzemię	vermę
noun - jimenьnik: "vermę" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	wrzemię	vermę
noun - jimenьnik: "vermę" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	wrzemienia	vermena
noun - jimenьnik: "vermę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	wrzemieniu	vermene
noun - jimenьnik: "vermę" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	wrzemieniu	vermeni
noun - jimenьnik: "vermę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	wrzemieniem	vermenimь
noun - jimenьnik: "vermę" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	wrzemię	vermę
noun - jimenьnik: "vermę" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	wrzemiona	vermena
noun - jimenьnik: "vermę" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	wrzemiona	vermena
noun - jimenьnik: "vermę" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	wrzemion	vermen
noun - jimenьnik: "vermę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	wrzemionach	vermenih
noun - jimenьnik: "vermę" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	wrzemionom	vermenim
noun - jimenьnik: "vermę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	wrzemionami	vermeny
noun - jimenьnik: "vermę" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	wrzemiona	vermena
noun - jimenьnik: "bermę" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	brzemię	bermę
noun - jimenьnik: "bermę" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	brzemię	bermę
noun - jimenьnik: "bermę" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	brzemienia	bermena
noun - jimenьnik: "bermę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	brzemieniu	bermene
noun - jimenьnik: "bermę" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	brzemieniu	bermeni
noun - jimenьnik: "bermę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	brzemieniem	bermenimь
noun - jimenьnik: "bermę" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burden	brzemię	bermę
noun - jimenьnik: "bermę" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	brzemiona	bermena
noun - jimenьnik: "bermę" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	brzemiona	bermena
noun - jimenьnik: "bermę" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	brzemion	bermen
noun - jimenьnik: "bermę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	brzemionach	bermenih
noun - jimenьnik: "bermę" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	brzemionom	bermenim
noun - jimenьnik: "bermę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	brzemionami	bermeny
noun - jimenьnik: "bermę" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	burdens	brzemiona	bermena
noun - jimenьnik: "jimeno" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	title	tytuł	jiměno
noun - jimenьnik: "jimeno" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	title	tytuł	jiměno
noun - jimenьnik: "jimeno" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	title	tytułu	jiměny
noun - jimenьnik: "jimeno" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	title	tytule	jiměně
noun - jimenьnik: "jimeno" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	title	tytułowi	jiměnu
noun - jimenьnik: "jimeno" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	title	tytułem	jiměnomь
noun - jimenьnik: "jimeno" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	title	tytule	jiměno
noun - jimenьnik: "jimeno" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	titles	tytuły	jiměna
noun - jimenьnik: "jimeno" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	titles	tytuły	jiměna
noun - jimenьnik: "jimeno" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	titles	tytułów	jiměn
noun - jimenьnik: "jimeno" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	titles	tytułach	jiměněh
noun - jimenьnik: "jimeno" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	titles	tytułom	jiměnom
noun - jimenьnik: "jimeno" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	titles	tytułami	jiměnami
noun - jimenьnik: "jimeno" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	titles	tytuły	jiměna
noun - jimenьnik: "jimeno" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	miano	jiměno
noun - jimenьnik: "jimeno" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	miano	jiměno
noun - jimenьnik: "jimeno" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	miana	jiměny
noun - jimenьnik: "jimeno" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	mianie	jiměně
noun - jimenьnik: "jimeno" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	mianu	jiměnu
noun - jimenьnik: "jimeno" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	mianem	jiměnomь
noun - jimenьnik: "jimeno" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	name	miano	jiměno
noun - jimenьnik: "jimeno" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	miana	jiměna
noun - jimenьnik: "jimeno" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	miana	jiměna
noun - jimenьnik: "jimeno" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	mian	jiměn
noun - jimenьnik: "jimeno" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	mianach	jiměněh
noun - jimenьnik: "jimeno" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	mianom	jiměnom
noun - jimenьnik: "jimeno" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	mianami	jiměnami
noun - jimenьnik: "jimeno" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	names	miana	jiměna
noun - jimenьnik: "rodьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwo	rodьstvo
noun - jimenьnik: "rodьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwo	rodьstvo
noun - jimenьnik: "rodьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwa	rodьstva
noun - jimenьnik: "rodьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwie	rodьstvě
noun - jimenьnik: "rodьstvo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwu	rodьstvu
noun - jimenьnik: "rodьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwem	rodьstvomь
noun - jimenьnik: "rodьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwo	rodьstvo
noun - jimenьnik: "rodьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwa	rodьstva
noun - jimenьnik: "rodьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwa	rodьstva
noun - jimenьnik: "rodьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztw	rodьstv
noun - jimenьnik: "rodьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwach	rodьstvěh
noun - jimenьnik: "rodьstvo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwom	rodьstvom
noun - jimenьnik: "rodьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwami	rodьstvy
noun - jimenьnik: "rodьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodztwa	rodьstva
noun - jimenьnik: "rodьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwo	rodьstvo
noun - jimenьnik: "rodьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwo	rodьstvo
noun - jimenьnik: "rodьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwa	rodьstva
noun - jimenьnik: "rodьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwie	rodьstvě
noun - jimenьnik: "rodьstvo" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwu	rodьstvu
noun - jimenьnik: "rodьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwem	rodьstvomь
noun - jimenьnik: "rodьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwo	rodьstvo
noun - jimenьnik: "rodьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwa	rodьstva
noun - jimenьnik: "rodьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwa	rodьstva
noun - jimenьnik: "rodьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństw	rodьstv
noun - jimenьnik: "rodьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwach	rodьstvěh
noun - jimenьnik: "rodьstvo" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwom	rodьstvom
noun - jimenьnik: "rodьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwami	rodьstvy
noun - jimenьnik: "rodьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	siblings	rodzeństwa	rodьstva
noun - jimenьnik: "protivьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversity	przeciwność	protivьnostь
noun - jimenьnik: "protivьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversity	przeciwność	protivьnostь
noun - jimenьnik: "protivьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversity	przeciwności	protivьnosti
noun - jimenьnik: "protivьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversity	przeciwności	protivьnosti
noun - jimenьnik: "protivьnostь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversity	przeciwności	protivьnosti
noun - jimenьnik: "protivьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversity	przeciwnością	protivьnostьjǫ
noun - jimenьnik: "protivьnostь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversity	przeciwności	protivьnosti
noun - jimenьnik: "protivьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversities	przeciwności	protivьnosti
noun - jimenьnik: "protivьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversities	przeciwności	protivьnosti
noun - jimenьnik: "protivьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversities	przeciwności	protivьnostь
noun - jimenьnik: "protivьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversities	przeciwnościach	protivьnostih
noun - jimenьnik: "protivьnostь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversities	przeciwnościom	protivьnostim
noun - jimenьnik: "protivьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversities	przeciwnościami	protivьnostьmi
noun - jimenьnik: "protivьnostь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	adversities	przeciwności	protivьnosti
noun - jimenьnik: "protivьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposite	przeciwieństwo	protivьnostь
noun - jimenьnik: "protivьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposite	przeciwieństwo	protivьnostь
noun - jimenьnik: "protivьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposite	przeciwieństwa	protivьnosti
noun - jimenьnik: "protivьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposite	przeciwieństwie	protivьnosti
noun - jimenьnik: "protivьnostь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposite	przeciwieństwu	protivьnosti
noun - jimenьnik: "protivьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposite	przeciwieństwem	protivьnostьjǫ
noun - jimenьnik: "protivьnostь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposite	przeciwieństwo	protivьnostь
noun - jimenьnik: "protivьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposites	przeciwieństwa	protivьnosti
noun - jimenьnik: "protivьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposites	przeciwieństwa	protivьnosti
noun - jimenьnik: "protivьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposites	przeciwieństw	protivьnostь
noun - jimenьnik: "protivьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposites	przeciwieństwach	protivьnostih
noun - jimenьnik: "protivьnostь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposites	przeciwieństwom	protivьnostim
noun - jimenьnik: "protivьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposites	przeciwieństwami	protivьnostьmi
noun - jimenьnik: "protivьnostь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	opposites	przeciwieństwa	protivьnosti
noun - jimenьnik: "agnę" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lamb	jagnię	agnę
noun - jimenьnik: "agnę" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lamb	jagnię	agnę
noun - jimenьnik: "agnę" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lamb	jagnięcia	agnęta
noun - jimenьnik: "agnę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lamb	jagnieciu	agnęnti
noun - jimenьnik: "agnę" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lamb	jagnieciu	agnęnti
noun - jimenьnik: "agnę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lamb	jagnięciem	agnęntimь
noun - jimenьnik: "agnę" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lamb	jagnię	agnę
noun - jimenьnik: "agnę" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lambs	jagnięta	agnęnta
noun - jimenьnik: "agnę" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lambs	jagnięta	agnęnta
noun - jimenьnik: "agnę" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lambs	jagniąt	agnęt
noun - jimenьnik: "agnę" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lambs	jagniętach	agnętih
noun - jimenьnik: "agnę" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lambs	jagniętom	agnętim
noun - jimenьnik: "agnę" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lambs	jagniętami	agnęty
noun - jimenьnik: "agnę" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (animate) - rodjajь nijaky (životьny)	lambs	jagnięta	agnęta
noun - jimenьnik: "edinak" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only child	jedynak	edinak
noun - jimenьnik: "edinak" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only child	jedynaka	edinaka
noun - jimenьnik: "edinak" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only child	jedynaka	edinaka
noun - jimenьnik: "edinak" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only child	jedynaku	edinacě
noun - jimenьnik: "edinak" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only child	jedynakowi	edinaku
noun - jimenьnik: "edinak" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only child	jedynakiem	edinakomь
noun - jimenьnik: "edinak" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only child	jedynaku	edinače
noun - jimenьnik: "edinak" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only children	jedynacy	edinaci
noun - jimenьnik: "edinak" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only children	jedynaków	edinaky
noun - jimenьnik: "edinak" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only children	jedynaków	edinak
noun - jimenьnik: "edinak" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only children	jedynakach	edinacěh
noun - jimenьnik: "edinak" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only children	jedynakom	edinakom
noun - jimenьnik: "edinak" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only children	jedynakami	edinaky
noun - jimenьnik: "edinak" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	only children	jedynacy	edinaci
noun - jimenьnik: "děd" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfather	dziad	děd
noun - jimenьnik: "děd" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfather	dziada	děda
noun - jimenьnik: "děd" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfather	dziada	děda
noun - jimenьnik: "děd" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfather	dziadu	dědě
noun - jimenьnik: "děd" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfather	dziadowi/dziadu	dědu
noun - jimenьnik: "děd" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfather	dziadem	dědomь
noun - jimenьnik: "děd" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfather	dziadzie/dziadu	děde
noun - jimenьnik: "děd" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfathers	dziadowie/dziady	dědi
noun - jimenьnik: "děd" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfathers	dziadów	dědy
noun - jimenьnik: "děd" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfathers	dziadów	děd
noun - jimenьnik: "děd" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfathers	dziadach	děděh
noun - jimenьnik: "děd" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfathers	dziadom	dědom
noun - jimenьnik: "děd" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfathers	dziadami	dědy
noun - jimenьnik: "děd" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grandfathers	dziadowie/dziady	dědi
noun - jimenьnik: "klěšč" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	tick	kleszcz	klěščь
noun - jimenьnik: "klěšč" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	tick	kleszcza	klěšča
noun - jimenьnik: "klěšč" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	tick	kleszcza	klěšča
noun - jimenьnik: "klěšč" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	tick	kleszczu	klěšču
noun - jimenьnik: "klěšč" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	tick	kleszczowi	klěšču
noun - jimenьnik: "klěšč" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	tick	kleszczem	klěščemь
noun - jimenьnik: "klěšč" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	tick	kleszczu	klěšče
noun - jimenьnik: "klěšč" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ticks	kleszcze	klěšči
noun - jimenьnik: "klěšč" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ticks	kleszcze	klěšče
noun - jimenьnik: "klěšč" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ticks	kleszczy	klěšči
noun - jimenьnik: "klěšč" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ticks	kleszczach	klěščih
noun - jimenьnik: "klěšč" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ticks	kleszczom	klěščem
noun - jimenьnik: "klěšč" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ticks	kleszczami	klěšči
noun - jimenьnik: "klěšč" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ticks	kleszcze	klěšči
noun - jimenьnik: "kadidlo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incense	kadzidło	kadidlo
noun - jimenьnik: "kadidlo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incense	kadzidło	kadidlo
noun - jimenьnik: "kadidlo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incense	kadzidła	kadidla
noun - jimenьnik: "kadidlo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incense	kadzidle	kadidlě
noun - jimenьnik: "kadidlo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incense	kadzidłu	kadidlu
noun - jimenьnik: "kadidlo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incense	kadzidłem	kadidlomь
noun - jimenьnik: "kadidlo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incense	kadzidło	kadidlo
noun - jimenьnik: "kadidlo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incenses	kadzidła	kadidla
noun - jimenьnik: "kadidlo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incenses	kadzidła	kadidla
noun - jimenьnik: "kadidlo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incenses	kadzideł	kadidl
noun - jimenьnik: "kadidlo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incenses	kadzidłach	kadidlěh
noun - jimenьnik: "kadidlo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incenses	kadzidłom	kadidlom
noun - jimenьnik: "kadidlo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incenses	kadzidłami	kadidly
noun - jimenьnik: "kadidlo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incenses	kadzidła	kadidla
noun - jimenьnik: "orvьnoležьnobok" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelogram	równoległobok	orvьnoležьnobok
noun - jimenьnik: "orvьnoležьnobok" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelogram	równoległobok	orvьnoležьnobok
noun - jimenьnik: "orvьnoležьnobok" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelogram	równoległoboku	orvьnoležьnoboka
noun - jimenьnik: "orvьnoležьnobok" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelogram	równoległoboku	orvьnoležьnoboku
noun - jimenьnik: "orvьnoležьnobok" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelogram	równoległobokowi	orvьnoležьnoboku
noun - jimenьnik: "orvьnoležьnobok" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelogram	równoległobokiem	orvьnoležьnobokomь
noun - jimenьnik: "orvьnoležьnobok" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelogram	równoległoboku	orvьnoležьnoboku
noun - jimenьnik: "orvьnoležьnobok" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelograms	równoległoboki	orvьnoležьnoboci
noun - jimenьnik: "orvьnoležьnobok" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelograms	równoległoboki	orvьnoležьnoboky
noun - jimenьnik: "orvьnoležьnobok" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelograms	równoległoboków	orvьnoležьnobok
noun - jimenьnik: "orvьnoležьnobok" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelograms	równoległobokach	orvьnoležьnobocěh
noun - jimenьnik: "orvьnoležьnobok" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelograms	równoległobokom	orvьnoležьnobokom
noun - jimenьnik: "orvьnoležьnobok" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelograms	równoległobokami	orvьnoležьnoboky
noun - jimenьnik: "orvьnoležьnobok" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallelograms	równoległoboki	orvьnoležьnoboci
noun - jimenьnik: "orvьnoležьnik" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallel	równoleżnik	orvьnoležьnik
noun - jimenьnik: "orvьnoležьnik" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallel	równoleżnik	orvьnoležьnik
noun - jimenьnik: "orvьnoležьnik" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallel	równoleżnika	orvьnoležьnika
noun - jimenьnik: "orvьnoležьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallel	równoleżniku	orvьnoležьnicě
noun - jimenьnik: "orvьnoležьnik" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallel	równoleżnikowi	orvьnoležьniku
noun - jimenьnik: "orvьnoležьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallel	równoleżnikiem	orvьnoležьnikomь
noun - jimenьnik: "orvьnoležьnik" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallel	równoleżniku	orvьnoležьniče
noun - jimenьnik: "orvьnoležьnik" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallels	równoleżniki	orvьnoležьnici
noun - jimenьnik: "orvьnoležьnik" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallels	równoleżniki	orvьnoležьniky
noun - jimenьnik: "orvьnoležьnik" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallels	równoleżników	orvьnoležьnik
noun - jimenьnik: "orvьnoležьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallels	równoleżnikach	orvьnoležьnicěh
noun - jimenьnik: "orvьnoležьnik" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallels	równoleżnikom	orvьnoležьnikom
noun - jimenьnik: "orvьnoležьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallels	równoleżnikami	orvьnoležьniky
noun - jimenьnik: "orvьnoležьnik" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	parallels	równoleżniki	orvьnoležьnici
noun - jimenьnik: "dolnь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palm	dłoń	dolnь
noun - jimenьnik: "dolnь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palm	dłoń	dolnь
noun - jimenьnik: "dolnь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palm	dłoni	dolni
noun - jimenьnik: "dolnь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palm	dłoni	dolni
noun - jimenьnik: "dolnь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palm	dłoni	dolni
noun - jimenьnik: "dolnь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palm	dłonią	dolnьjǫ
noun - jimenьnik: "dolnь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palm	dłoni	dolni
noun - jimenьnik: "dolnь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palms	dłonie	dolni
noun - jimenьnik: "dolnь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palms	dłonie	dolni
noun - jimenьnik: "dolnь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palms	dłoni	dolnь
noun - jimenьnik: "dolnь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palms	dłoniach	dolnih
noun - jimenьnik: "dolnь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palms	dłoniom	dolnim
noun - jimenьnik: "dolnь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palms	dłońmi	dolnьmi
noun - jimenьnik: "dolnь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	palms	dłonie	dolni
noun - jimenьnik: "pribor do ědla" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutlery	sztuciec	pribor do ědla
noun - jimenьnik: "pribor do ědla" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutlery	sztuciec	pribor do ědla
noun - jimenьnik: "pribor do ědla" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutlery	sztućca	pribora do ědla
noun - jimenьnik: "pribor do ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutlery	sztućcu	priborě do ědla
noun - jimenьnik: "pribor do ědla" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutlery	sztućcowi	priboru do ědla
noun - jimenьnik: "pribor do ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutlery	sztućcem	priboromь do ědla
noun - jimenьnik: "pribor do ědla" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutlery	sztuciec	pribor do ědla
noun - jimenьnik: "pribor do ědla" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutleries	sztućce	pribori do ědla
noun - jimenьnik: "pribor do ědla" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutleries	sztućce	pribori do ědla
noun - jimenьnik: "pribor do ědla" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutleries	sztućców	pribor do ědla
noun - jimenьnik: "pribor do ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutleries	sztućcach	priborěh do ědla
noun - jimenьnik: "pribor do ědla" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutleries	sztućcom	priborom do ědla
noun - jimenьnik: "pribor do ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutleries	sztućcami	pribory do ědla
noun - jimenьnik: "pribor do ědla" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cutleries	sztućce	pribori do ědla
noun - jimenьnik: "pribor do ědla" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przybór do jedzenia	pribor do ědla
noun - jimenьnik: "pribor do ědla" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przybór do jedzenia	pribor do ědla
noun - jimenьnik: "pribor do ědla" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyboru do jedzenia	pribora do ědla
noun - jimenьnik: "pribor do ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyborze do jedzenia	priborě do ědla
noun - jimenьnik: "pribor do ědla" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyborowi do jedzenia	priboru do ědla
noun - jimenьnik: "pribor do ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyborem do jedzenia	priboromь do ědla
noun - jimenьnik: "pribor do ědla" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przybór do jedzenia	pribor do ědla
noun - jimenьnik: "pribor do ědla" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przybory do jedzenia	pribori do ědla
noun - jimenьnik: "pribor do ědla" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przybory do jedzenia	pribori do ědla
noun - jimenьnik: "pribor do ědla" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborów do jedzenia	pribor do ědla
noun - jimenьnik: "pribor do ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborach do jedzenia	priborěh do ědla
noun - jimenьnik: "pribor do ědla" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborom do jedzenia	priborom do ědla
noun - jimenьnik: "pribor do ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborami do jedzenia	pribory do ědla
noun - jimenьnik: "pribor do ědla" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przybory do jedzenia	pribori do ědla
noun - jimenьnik: "pribor do ědla" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przybór do jadła	pribor do ědla
noun - jimenьnik: "pribor do ědla" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przybór do jadła	pribor do ědla
noun - jimenьnik: "pribor do ědla" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyboru do jadła	pribora do ědla
noun - jimenьnik: "pribor do ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyborze do jadła	priborě do ědla
noun - jimenьnik: "pribor do ědla" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyborowi do jadła	priboru do ědla
noun - jimenьnik: "pribor do ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przyborem do jadła	priboromь do ědla
noun - jimenьnik: "pribor do ědla" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensil	przybór do jadła	pribor do ědla
noun - jimenьnik: "pribor do ědla" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przybory do jadła	pribori do ědla
noun - jimenьnik: "pribor do ědla" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przybory do jadła	pribori do ědla
noun - jimenьnik: "pribor do ědla" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborów do jadła	pribor do ědla
noun - jimenьnik: "pribor do ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborach do jadła	priborěh do ědla
noun - jimenьnik: "pribor do ědla" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborom do jadła	priborom do ědla
noun - jimenьnik: "pribor do ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przyborami do jadła	pribory do ědla
noun - jimenьnik: "pribor do ědla" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	eating utensils	przybory do jadła	pribori do ědla
noun - jimenьnik: "pribor" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensil	przybór	pribor
noun - jimenьnik: "pribor" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensil	przybór	pribor
noun - jimenьnik: "pribor" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensil	przyboru	pribora
noun - jimenьnik: "pribor" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensil	przyborze	priborě
noun - jimenьnik: "pribor" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensil	przyborowi	priboru
noun - jimenьnik: "pribor" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensil	przyborem	priboromь
noun - jimenьnik: "pribor" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensil	przybór	pribor
noun - jimenьnik: "pribor" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensils	przybory	pribori
noun - jimenьnik: "pribor" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensils	przybory	pribori
noun - jimenьnik: "pribor" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensils	przyborów	pribor
noun - jimenьnik: "pribor" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensils	przyborach	priborěh
noun - jimenьnik: "pribor" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensils	przyborom	priborom
noun - jimenьnik: "pribor" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensils	przyborami	pribory
noun - jimenьnik: "pribor" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	utensils	przybory	pribori
noun - jimenьnik: "supisu ědla" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spis jadła	supis ědla
noun - jimenьnik: "supisu ědla" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spis jadła	supis ědla
noun - jimenьnik: "supisu ědla" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisu jadła	supisa ědla
noun - jimenьnik: "supisu ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisie jadła	supisě ědla
noun - jimenьnik: "supisu ědla" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisowi jadła	supisu ědla
noun - jimenьnik: "supisu ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisem jadła	supisomь ědla
noun - jimenьnik: "supisu ědla" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisie jadła	supise ědla
noun - jimenьnik: "supisu ědla" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisy jadła	supisi ědla
noun - jimenьnik: "supisu ědla" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisy jadła	supisy ědla
noun - jimenьnik: "supisu ědla" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisów jadła	supis ědla
noun - jimenьnik: "supisu ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisach jadła	supisěh ědla
noun - jimenьnik: "supisu ědla" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisom jadła	supisom ědla
noun - jimenьnik: "supisu ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisami jadła	supisy ědla
noun - jimenьnik: "supisu ědla" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisy jadła	supisi ědla
noun - jimenьnik: "supisu ědla" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spis jedzenia	supis ědla
noun - jimenьnik: "supisu ědla" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spis jedzenia	supis ědla
noun - jimenьnik: "supisu ědla" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisu jedzenia	supisa ědla
noun - jimenьnik: "supisu ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisie jedzenia	supisě ědla
noun - jimenьnik: "supisu ědla" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisowi jedzenia	supisu ědla
noun - jimenьnik: "supisu ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisem jedzenia	supisomь ědla
noun - jimenьnik: "supisu ědla" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menu	spisie jedzenia	supise ědla
noun - jimenьnik: "supisu ědla" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisy jedzenia	supisi ědla
noun - jimenьnik: "supisu ědla" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisy jedzenia	supisy ědla
noun - jimenьnik: "supisu ědla" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisów jedzenia	supis ědla
noun - jimenьnik: "supisu ědla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisach jedzenia	supisěh ědla
noun - jimenьnik: "supisu ědla" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisom jedzenia	supisom ědla
noun - jimenьnik: "supisu ědla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisami jedzenia	supisy ědla
noun - jimenьnik: "supisu ědla" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	menus	spisy jedzenia	supisi ědla
noun - jimenьnik: "migla" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mist	mgła	migla
noun - jimenьnik: "migla" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mist	mgłę	miglǫ
noun - jimenьnik: "migla" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mist	mgły	migly
noun - jimenьnik: "migla" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mist	mgle	miglě
noun - jimenьnik: "migla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mist	mgłą	miglojǫ
noun - jimenьnik: "migla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mist	mgle	miglě
noun - jimenьnik: "migla" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mist	mgło	miglo
noun - jimenьnik: "migla" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mists	mgły	migly
noun - jimenьnik: "migla" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mists	mgły	migly
noun - jimenьnik: "migla" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mists	mgieł	migl
noun - jimenьnik: "migla" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mists	mgłom	miglam
noun - jimenьnik: "migla" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mists	mgłami	miglami
noun - jimenьnik: "migla" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mists	mgłach	miglah
noun - jimenьnik: "migla" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	mists	mgły	migly
noun - jimenьnik: "rězьba" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculpture	rzeźba	rězьba
noun - jimenьnik: "rězьba" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculpture	rzeźbę	rězьbǫ
noun - jimenьnik: "rězьba" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculpture	rzeźby	rězьby
noun - jimenьnik: "rězьba" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculpture	rzeźbie	rězьbě
noun - jimenьnik: "rězьba" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculpture	rzeźbą	rězьbojǫ
noun - jimenьnik: "rězьba" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculpture	rzeźbie	rězьbě
noun - jimenьnik: "rězьba" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculpture	rzeźbo	rězьbo
noun - jimenьnik: "rězьba" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculptures	rzeźby	rězьby
noun - jimenьnik: "rězьba" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculptures	rzeźby	rězьby
noun - jimenьnik: "rězьba" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculptures	rzeźb	rězьb
noun - jimenьnik: "rězьba" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculptures	rzeźbom	rězьbam
noun - jimenьnik: "rězьba" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculptures	rzeźbami	rězьbami
noun - jimenьnik: "rězьba" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculptures	rzeźbach	rězьbah
noun - jimenьnik: "rězьba" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	sculptures	rzeźby	rězьby
noun - jimenьnik: "rězьba" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stucco	sztukateria	rězьba
noun - jimenьnik: "rězьba" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stucco	sztukaterię	rězьbǫ
noun - jimenьnik: "rězьba" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stucco	sztukaterii	rězьby
noun - jimenьnik: "rězьba" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stucco	sztukaterii	rězьbě
noun - jimenьnik: "rězьba" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stucco	sztukaterią	rězьbojǫ
noun - jimenьnik: "rězьba" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stucco	sztukaterii	rězьbě
noun - jimenьnik: "rězьba" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stucco	sztukaterio	rězьbo
noun - jimenьnik: "rězьba" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stuccos	sztukaterie	rězьby
noun - jimenьnik: "rězьba" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stuccos	sztukaterie	rězьby
noun - jimenьnik: "rězьba" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stuccos	sztukaterii	rězьb
noun - jimenьnik: "rězьba" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stuccos	sztukateriom	rězьbam
noun - jimenьnik: "rězьba" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stuccos	sztukateriami	rězьbami
noun - jimenьnik: "rězьba" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stuccos	sztukateriach	rězьbah
noun - jimenьnik: "rězьba" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	stuccos	sztukaterie	rězьby
noun - jimenьnik: "zorja" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	aurora	zorza	zorja
noun - jimenьnik: "zorja" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	aurora	zorzę	zorjǫ
noun - jimenьnik: "zorja" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	aurora	zorzy	zorji
noun - jimenьnik: "zorja" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	aurora	zorzy	zorji
noun - jimenьnik: "zorja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	aurora	zorzą	zorjejǫ
noun - jimenьnik: "zorja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	aurora	zorzy	zorji
noun - jimenьnik: "zorja" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	aurora	zorzo	zorjo
noun - jimenьnik: "zorja" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	auroras	zorze	zorě
noun - jimenьnik: "zorja" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	auroras	zorze	zorě
noun - jimenьnik: "zorja" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	auroras	zórz	zorj
noun - jimenьnik: "zorja" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	auroras	zorzom	zorjam
noun - jimenьnik: "zorja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	auroras	zorzami	zorjami
noun - jimenьnik: "zorja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	auroras	zorzach	zorjah
noun - jimenьnik: "zorja" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	auroras	zorze	zorě
noun - jimenьnik: "zova" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	call	zwa	zova
noun - jimenьnik: "zova" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	call	zwę	zovǫ
noun - jimenьnik: "zova" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	call	zwy	zovy
noun - jimenьnik: "zova" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	call	zwie	zově
noun - jimenьnik: "zova" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	call	zwą	zovojǫ
noun - jimenьnik: "zova" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	call	zwie	zově
noun - jimenьnik: "zova" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	call	zwo	zovo
noun - jimenьnik: "zova" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	calls	zwy	zovy
noun - jimenьnik: "zova" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	calls	zwy	zovy
noun - jimenьnik: "zova" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	calls	zw	zov
noun - jimenьnik: "zova" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	calls	zwom	zovam
noun - jimenьnik: "zova" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	calls	zwami	zovami
noun - jimenьnik: "zova" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	calls	zwach	zovah
noun - jimenьnik: "zova" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	calls	zwy	zovy
noun - jimenьnik: "zova" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	name	nazwa	zova
noun - jimenьnik: "zova" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	name	nazwę	zovǫ
noun - jimenьnik: "zova" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	name	nazwy	zovy
noun - jimenьnik: "zova" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	name	nazwie	zově
noun - jimenьnik: "zova" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	name	nazwą	zovojǫ
noun - jimenьnik: "zova" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	name	nazwie	zově
noun - jimenьnik: "zova" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	name	nazwo	zovo
noun - jimenьnik: "zova" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	names	nazwy	zovy
noun - jimenьnik: "zova" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	names	nazwy	zovy
noun - jimenьnik: "zova" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	names	nazw	zov
noun - jimenьnik: "zova" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	names	nazwom	zovam
noun - jimenьnik: "zova" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	names	nazwami	zovami
noun - jimenьnik: "zova" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	names	nazwach	zovah
noun - jimenьnik: "zova" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	names	nazwy	zovy
noun - jimenьnik: "zovanьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	calling	zwanie	zovanьje
noun - jimenьnik: "zovanьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	calling	zwanie	zovanьje
noun - jimenьnik: "zovanьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	calling	zwania	zovanьja
noun - jimenьnik: "zovanьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	calling	zwaniu	zovanьju
noun - jimenьnik: "zovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	calling	zwaniem	zovanьjemь
noun - jimenьnik: "zovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	calling	zwaniu	zovanьji
noun - jimenьnik: "zovanьje" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	calling	zwanie	zovanьje
noun - jimenьnik: "zovanьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	callings	zwania	zovanьja
noun - jimenьnik: "zovanьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	callings	zwania	zovanьja
noun - jimenьnik: "zovanьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	callings	zwań	zovanij
noun - jimenьnik: "zovanьje" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	callings	zwaniom	zovanьjem
noun - jimenьnik: "zovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	callings	zwaniami	zovanьji
noun - jimenьnik: "zovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	callings	zwaniach	zovanьjih
noun - jimenьnik: "zovanьje" | vocative - zovateljь (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	callings	zwania	zovanьja
noun - jimenьnik: "zovanьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	nazywanie	zovanьje
noun - jimenьnik: "zovanьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	nazywanie	zovanьje
noun - jimenьnik: "zovanьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	nazywania	zovanьja
noun - jimenьnik: "zovanьje" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	nazywaniu	zovanьju
noun - jimenьnik: "zovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	nazywaniem	zovanьjem
noun - jimenьnik: "zovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	nazywaniu	zovanьji
noun - jimenьnik: "zovanьje" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	naming	nazywanie	zovanьje
noun - jimenьnik: "zovanьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	nazywania	zovanьja
noun - jimenьnik: "zovanьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	nazywania	zovanьja
noun - jimenьnik: "zovanьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	nazywań	zovanij
noun - jimenьnik: "zovanьje" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	nazywaniom	zovanьjem
noun - jimenьnik: "zovanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	nazywaniami	zovanьji
noun - jimenьnik: "zovanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	nazywaniach	zovanьjih
noun - jimenьnik: "zovanьje" | vocative - zovateljь (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	namings	nazywania	zovanьja
noun - jimenьnik: "tokarka" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathe	tokarka	tokarka
noun - jimenьnik: "tokarka" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathe	tokarkę	tokarkǫ
noun - jimenьnik: "tokarka" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathe	tokarki	tokarky
noun - jimenьnik: "tokarka" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathe	tokarce	tokarkě
noun - jimenьnik: "tokarka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathe	tokarką	tokarkojǫ
noun - jimenьnik: "tokarka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathe	tokarce	tokarkě
noun - jimenьnik: "tokarka" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathe	tokarko	tokarko
noun - jimenьnik: "tokarka" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathes	tokarki	tokarky
noun - jimenьnik: "tokarka" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathes	tokarki	tokarky
noun - jimenьnik: "tokarka" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathes	tokarek	tokark
noun - jimenьnik: "tokarka" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathes	tokarkom	tokarkam
noun - jimenьnik: "tokarka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathes	tokarkami	tokarkami
noun - jimenьnik: "tokarka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathes	tokarkach	tokarkah
noun - jimenьnik: "tokarka" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	lathes	tokarki	tokarky
noun - jimenьnik: "nesučęstьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	misfortune	nieszczęście	nesučęstьje
noun - jimenьnik: "nesučęstьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	misfortune	nieszczęście	nesučęstьje
noun - jimenьnik: "nesučęstьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	misfortune	nieszczęścia	nesučęstьja
noun - jimenьnik: "nesučęstьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	misfortune	nieszczęściu	nesučęstьju
noun - jimenьnik: "nesučęstьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	misfortune	nieszczęściem	nesučęstьjemь
noun - jimenьnik: "nesučęstьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	misfortune	nieszczęściu	nesučęstьji
noun - jimenьnik: "nesučęstьje" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	misfortune	nieszczęście	nesučęstьje
noun - jimenьnik: "nesučęstьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	catastrophe	katastrofa	nesučęstьje
noun - jimenьnik: "nesučęstьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	catastrophe	katastrofę	nesučęstьje
noun - jimenьnik: "nesučęstьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	catastrophe	katastrofy	nesučęstьja
noun - jimenьnik: "nesučęstьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	catastrophe	katastrofie	nesučęstьju
noun - jimenьnik: "nesučęstьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	catastrophe	katastrofą	nesučęstьjemь
noun - jimenьnik: "nesučęstьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	catastrophe	katastrofie	nesučęstьji
noun - jimenьnik: "nesučęstьje" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	catastrophe	katastrofo	nesučęstьje
noun - jimenьnik: "nesučęstьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	tragedy	tragedia	nesučęstьje
noun - jimenьnik: "nesučęstьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	tragedy	tragedię	nesučęstьje
noun - jimenьnik: "nesučęstьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	tragedy	tragedii	nesučęstьja
noun - jimenьnik: "nesučęstьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	tragedy	tragedii	nesučęstьju
noun - jimenьnik: "nesučęstьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	tragedy	tragedią	nesučęstьjemь
noun - jimenьnik: "nesučęstьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	tragedy	tragedii	nesučęstьji
noun - jimenьnik: "nesučęstьje" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	tragedy	tragedio	nesučęstьje
noun - jimenьnik: "směšek" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	śmieszek	směšek
noun - jimenьnik: "směšek" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	śmieszka	směšeka
noun - jimenьnik: "směšek" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	śmieszka	směšeka
noun - jimenьnik: "směšek" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	śmieszkowi	směšeku
noun - jimenьnik: "směšek" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	śmieszkiem	směšekomь
noun - jimenьnik: "směšek" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	śmieszku	směšeku
noun - jimenьnik: "směšek" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	śmieszku	směšče
noun - jimenьnik: "směšek" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	żartowniś	směšok
noun - jimenьnik: "směšek" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	żartownisia	směšeka
noun - jimenьnik: "směšek" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	żartownisia	směšeka
noun - jimenьnik: "směšek" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	żartownisiowi	směšeku
noun - jimenьnik: "směšek" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	żartownisiem	směšekomь
noun - jimenьnik: "směšek" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	żartownisiu	směšeku
noun - jimenьnik: "směšek" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	żartownisiu	směšče
noun - jimenьnik: "směšek" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	jajcarz	směšok
noun - jimenьnik: "směšek" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	jajcarza	směšeka
noun - jimenьnik: "směšek" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	jajcarza	směšeka
noun - jimenьnik: "směšek" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	jajcarzowi	směšeku
noun - jimenьnik: "směšek" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	jajcarzem	směšekomь
noun - jimenьnik: "směšek" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	jajcarzu	směšeku
noun - jimenьnik: "směšek" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	joker	jajcarzu	směšče
noun - jimenьnik: "melkarjь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkman	mleczarz	melkarjь
noun - jimenьnik: "melkarjь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkman	mleczarza	melkarja
noun - jimenьnik: "melkarjь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkman	mleczarza	melkarja
noun - jimenьnik: "melkarjь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkman	mleczarzowi/mleczarzu	melkarju
noun - jimenьnik: "melkarjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkman	mleczarzu	melkarji
noun - jimenьnik: "melkarjь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkman	mleczarzem	melkarjemь
noun - jimenьnik: "melkarjь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkman	mleczarzu	melkarju
noun - jimenьnik: "melkarjь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkmen	mleczarze	melkarji
noun - jimenьnik: "melkarjь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkmen	mleczarzy	melkarje
noun - jimenьnik: "melkarjь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkmen	mleczarzy	melkarji
noun - jimenьnik: "melkarjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkmen	mleczarzach	melkarjih
noun - jimenьnik: "melkarjь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkmen	mleczarzom	melkarjem
noun - jimenьnik: "melkarjь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkmen	mleczarzami	melkarji
noun - jimenьnik: "melkarjь" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	milkmen	mleczarze	melkarji
noun - jimenьnik: "počętok" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	start	start	počętok
noun - jimenьnik: "počętok" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	start	start	počętok
noun - jimenьnik: "počętok" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	start	startu	počętoka
noun - jimenьnik: "počętok" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	start	startowi	počętoku
noun - jimenьnik: "počętok" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	start	startem	počętokomь
noun - jimenьnik: "počętok" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	start	starcie	počętoku
noun - jimenьnik: "počętok" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	start	starcie	počętoče
noun - jimenьnik: "stroježь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangement	układ	stroježь
noun - jimenьnik: "stroježь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangement	układ	stroježь
noun - jimenьnik: "stroježь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangement	układu	stroježa
noun - jimenьnik: "stroježь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangement	układzie	stroježi
noun - jimenьnik: "stroježь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangement	układowi	stroježu
noun - jimenьnik: "stroježь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangement	układem	stroježemь
noun - jimenьnik: "stroježь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangement	układzie	stroježu
noun - jimenьnik: "stroježь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangements	układy	stroježi
noun - jimenьnik: "stroježь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangements	układy	stroježi
noun - jimenьnik: "stroježь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangements	układów	stroježi
noun - jimenьnik: "stroježь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangements	układach	stroježih
noun - jimenьnik: "stroježь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangements	układom	stroježem
noun - jimenьnik: "stroježь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangements	układami	stroježi
noun - jimenьnik: "stroježь" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	arrangements	układy	stroježi
noun - jimenьnik: "stroježь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structure	struktura	stroježь
noun - jimenьnik: "stroježь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structure	strukturę	stroježь
noun - jimenьnik: "stroježь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structure	struktury	stroježa
noun - jimenьnik: "stroježь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structure	strukturze	stroježi
noun - jimenьnik: "stroježь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structure	strukturze	stroježu
noun - jimenьnik: "stroježь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structure	strukturą	stroježemь
noun - jimenьnik: "stroježь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structure	strukturo	stroježu
noun - jimenьnik: "stroježь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structures	struktury	stroježi
noun - jimenьnik: "stroježь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structures	struktury	stroježi
noun - jimenьnik: "stroježь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structures	struktur	stroježi
noun - jimenьnik: "stroježь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structures	strukturach	stroježih
noun - jimenьnik: "stroježь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structures	strukturom	stroježem
noun - jimenьnik: "stroježь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structures	strukturami	stroježi
noun - jimenьnik: "stroježь" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	structures	struktury	stroježi
noun - jimenьnik: "stroježь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guard	strojeż	stroježь
noun - jimenьnik: "stroježь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guard	strojeż	stroježь
noun - jimenьnik: "stroježь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guard	strojeża	stroježa
noun - jimenьnik: "stroježь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guard	strojeżu	stroježi
noun - jimenьnik: "stroježь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guard	strojeżu	stroježu
noun - jimenьnik: "stroježь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guard	strojeżem	stroježemь
noun - jimenьnik: "stroježь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guard	strojeżu	stroježu
noun - jimenьnik: "stroježь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guards	strojeże	stroježi
noun - jimenьnik: "stroježь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guards	strojeże	stroježi
noun - jimenьnik: "stroježь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guards	strojeży	stroježi
noun - jimenьnik: "stroježь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guards	strojeżach	stroježih
noun - jimenьnik: "stroježь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guards	strojeżom	stroježem
noun - jimenьnik: "stroježь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guards	strojeżami	stroježi
noun - jimenьnik: "stroježь" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	guards	strojeże	stroježi
noun - jimenьnik: "skakalьc" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshopper	konik polny	skakalьcь
noun - jimenьnik: "skakalьc" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshopper	konika polnego	skakalьca
noun - jimenьnik: "skakalьc" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshopper	konika polnego	skakalьca
noun - jimenьnik: "skakalьc" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshopper	koniku polnym	skakalьci
noun - jimenьnik: "skakalьc" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshopper	konikowi polnemu	skakalьcu
noun - jimenьnik: "skakalьc" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshopper	konikiem polnym	skakalьcemь
noun - jimenьnik: "skakalьc" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshopper	koniku polny	skakalьče
noun - jimenьnik: "skakalьc" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshoppers	koniki polne	skakalьci
noun - jimenьnik: "skakalьc" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshoppers	koniki polne	skakalьce
noun - jimenьnik: "skakalьc" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshoppers	koników polnych	skakalьci
noun - jimenьnik: "skakalьc" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshoppers	konikach polnych	skakalьcih
noun - jimenьnik: "skakalьc" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshoppers	konikom polnym	skakalьcem
noun - jimenьnik: "skakalьc" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshoppers	konikami polnymi	skakalьci
noun - jimenьnik: "skakalьc" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	grasshoppers	koniki polne	skakalьci
noun - jimenьnik: "skakalьc" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumper	skakalec	skakalьcь
noun - jimenьnik: "skakalьc" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumper	skakalca	skakalьca
noun - jimenьnik: "skakalьc" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumper	skakalca	skakalьca
noun - jimenьnik: "skakalьc" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumper	skakalcu	skakalьci
noun - jimenьnik: "skakalьc" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumper	skakalcowi	skakalьcu
noun - jimenьnik: "skakalьc" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumper	skakalcem	skakalьcemь
noun - jimenьnik: "skakalьc" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumper	skakalcu	skakalьče
noun - jimenьnik: "skakalьc" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumpers	skakalcy	skakalьci
noun - jimenьnik: "skakalьc" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumpers	skakalców	skakalьce
noun - jimenьnik: "skakalьc" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumpers	skakalców	skakalьci
noun - jimenьnik: "skakalьc" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumpers	skakalcach	skakalьcih
noun - jimenьnik: "skakalьc" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumpers	skakalcom	skakalьcem
noun - jimenьnik: "skakalьc" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumpers	skakalcami	skakalьci
noun - jimenьnik: "skakalьc" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	jumpers	skakalcy	skakalьci
noun - jimenьnik: "nastrojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambience, mood, tuning	nastrój	nastrojь
noun - jimenьnik: "nastrojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambience, mood, tuning	nastrój	nastrojь
noun - jimenьnik: "nastrojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambience, mood, tuning	nastroju	nastroja
noun - jimenьnik: "nastrojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambience, mood, tuning	nastróju	nastroji
noun - jimenьnik: "nastrojь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambience, mood, tuning	nastrojowi/nastroju	nastroju
noun - jimenьnik: "nastrojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambience, mood, tuning	nastrojem	nastrojemь
noun - jimenьnik: "nastrojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambience, mood, tuning	nastroju	nastroju
noun - jimenьnik: "nastrojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambiences, moods, tunings	nastroje	nastroji
noun - jimenьnik: "nastrojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambiences, moods, tunings	nastroje	nastroje
noun - jimenьnik: "nastrojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambiences, moods, tunings	nastrojów/nastroi	nastroji
noun - jimenьnik: "nastrojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambiences, moods, tunings	nastrojach	nastrojih
noun - jimenьnik: "nastrojь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambiences, moods, tunings	nastrojem	nastrojem
noun - jimenьnik: "nastrojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambiences, moods, tunings	nastrojami	nastroji
noun - jimenьnik: "nastrojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ambiences, moods, tunings	nastroje	nastroji
noun - jimenьnik: "nastrojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambience, mood, tuning	nastrojenie	nastrojь
noun - jimenьnik: "nastrojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambience, mood, tuning	nastrojenie	nastrojь
noun - jimenьnik: "nastrojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambience, mood, tuning	nastrojenia	nastroja
noun - jimenьnik: "nastrojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambience, mood, tuning	nastrojeniu	nastroji
noun - jimenьnik: "nastrojь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambience, mood, tuning	nastrojeniu	nastroju
noun - jimenьnik: "nastrojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambience, mood, tuning	nastrojeniem	nastrojemь
noun - jimenьnik: "nastrojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambience, mood, tuning	nastrojenie	nastroju
noun - jimenьnik: "nastrojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambiences, moods, tunings	nastrojenia	nastroji
noun - jimenьnik: "nastrojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambiences, moods, tunings	nastrojenia	nastroje
noun - jimenьnik: "nastrojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambiences, moods, tunings	nastrojeń	nastroji
noun - jimenьnik: "nastrojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambiences, moods, tunings	nastrojeniach	nastrojih
noun - jimenьnik: "nastrojь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambiences, moods, tunings	nastrojeniom	nastrojem
noun - jimenьnik: "nastrojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambiences, moods, tunings	nastrojeniami	nastroji
noun - jimenьnik: "nastrojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ambiences, moods, tunings	nastrojenia	nastroji
noun - jimenьnik: "vojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier	żołnierz	vojь
noun - jimenьnik: "vojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier	żołnierza	voja
noun - jimenьnik: "vojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier	żołnierza	voja
noun - jimenьnik: "vojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier	żołnierzu	voji
noun - jimenьnik: "vojь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier	żołnierzowi	voju
noun - jimenьnik: "vojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier	żołnierzem	vojemь
noun - jimenьnik: "vojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier	żołnierzu	voju
noun - jimenьnik: "vojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers	żołnierze	voji
noun - jimenьnik: "vojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers	żołnierzy	voje
noun - jimenьnik: "vojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers	żołnierzy	voji
noun - jimenьnik: "vojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers	żołnierzach	vojih
noun - jimenьnik: "vojь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers	żołnierzom	vojem
noun - jimenьnik: "vojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers	żołnierzami	voji
noun - jimenьnik: "vojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers	żołnierze	voji
noun - jimenьnik: "vojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier, warrior	woj	vojь
noun - jimenьnik: "vojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier, warrior	woja	voja
noun - jimenьnik: "vojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier, warrior	woja	voja
noun - jimenьnik: "vojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier, warrior	woju	voji
noun - jimenьnik: "vojь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier, warrior	wojowi	voju
noun - jimenьnik: "vojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier, warrior	wojem	vojemь
noun - jimenьnik: "vojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldier, warrior	woju	voju
noun - jimenьnik: "vojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers, warriors	woje/wojowie	voji
noun - jimenьnik: "vojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers, warriors	woje/wojowie	voje
noun - jimenьnik: "vojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers, warriors	wojów/woi	voji
noun - jimenьnik: "vojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers, warriors	wojach	vojih
noun - jimenьnik: "vojь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers, warriors	wojom	vojem
noun - jimenьnik: "vojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers, warriors	wojami	voji
noun - jimenьnik: "vojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	soldiers, warriors	woje	voji
noun - jimenьnik: "pisanьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writing	pisanie	pisanьje
noun - jimenьnik: "pisanьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writing	pisanie	pisanьje
noun - jimenьnik: "pisanьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writing	pisania	pisanьja
noun - jimenьnik: "pisanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writing	pisaniu	pisanьji
noun - jimenьnik: "pisanьje" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writing	pisaniu	pisanьju
noun - jimenьnik: "pisanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writing	pisaniem	pisanьjemь
noun - jimenьnik: "pisanьje" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writing	pisanie	pisanьje
noun - jimenьnik: "pisanьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writings	pisania	pisanьja
noun - jimenьnik: "pisanьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writings	pisania	pisanьja
noun - jimenьnik: "pisanьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writings	pisań	pisanьji
noun - jimenьnik: "pisanьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writings	pisaniach	pisanьjih
noun - jimenьnik: "pisanьje" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writings	pisaniom	pisanьjem
noun - jimenьnik: "pisanьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writings	pisaniami	pisanьji
noun - jimenьnik: "pisanьje" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	writings	pisania	pisanьja
noun - jimenьnik: "pohodьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origin	pochodzenie	pohodьstvo
noun - jimenьnik: "pohodьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origin	pochodzenie	pohodьstvo
noun - jimenьnik: "pohodьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origin	pochodzenia	pohodьstva
noun - jimenьnik: "pohodьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origin	pochodzeniu	pohodьstvě
noun - jimenьnik: "pohodьstvo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origin	pochodzeniu	pohodьstvu
noun - jimenьnik: "pohodьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origin	pochodzeniem	pohodьstvomь
noun - jimenьnik: "pohodьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origin	pochodzenie	pohodьstvo
noun - jimenьnik: "pohodьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origins	pochodzenia	pohodьstva
noun - jimenьnik: "pohodьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origins	pochodzenia	pohodьstva
noun - jimenьnik: "pohodьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origins	pochodzeń	pohodьstv
noun - jimenьnik: "pohodьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origins	pochodzeniach	pohodьstvěh
noun - jimenьnik: "pohodьstvo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origins	pochodzeniom	pohodьstvom
noun - jimenьnik: "pohodьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origins	pochodzeniami	pohodьstvy
noun - jimenьnik: "pohodьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	origins	pochodzenia	pohodьstva
noun - jimenьnik: "zavistь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	envy	zawiść	zavistь
noun - jimenьnik: "zavistь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	envy	zawiść	zavistь
noun - jimenьnik: "zavistь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	envy	zawiści	zavisti
noun - jimenьnik: "zavistь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	envy	zawiści	zavisti
noun - jimenьnik: "zavistь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	envy	zawiścią	zavistьjǫ
noun - jimenьnik: "zavistь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	envy	zawiści	zavisti
noun - jimenьnik: "zavistь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	envy	zawiści	zavisti
noun - jimenьnik: "zavistь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	jealousy	zazdrość	zavistь
noun - jimenьnik: "zavistь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	jealousy	zazdrość	zavistь
noun - jimenьnik: "zavistь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	jealousy	zazdrości	zavisti
noun - jimenьnik: "zavistь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	jealousy	zazdrości	zavisti
noun - jimenьnik: "zavistь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	jealousy	zazdrością	zavistьjǫ
noun - jimenьnik: "zavistь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	jealousy	zazdrości	zavisti
noun - jimenьnik: "zavistь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	jealousy	zazdrości	zavisti
noun - jimenьnik: "svět" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	world	świat	svět
noun - jimenьnik: "svět" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	world	świat	svět
noun - jimenьnik: "svět" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	world	świata	světa
noun - jimenьnik: "svět" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	world	świecie	světě
noun - jimenьnik: "svět" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	world	światu/światowi	světu
noun - jimenьnik: "svět" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	world	światem	světomь
noun - jimenьnik: "svět" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	world	świecie	světe
noun - jimenьnik: "svět" | nominative - jimenovьnik (koto? čьto?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	worlds	światy	světi
noun - jimenьnik: "svět" | accusative - vinьnik (kogo? čьto?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	worlds	światy	světy
noun - jimenьnik: "svět" | genitive - rodilьnik (kogo? čego?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	worlds	światów	svět
noun - jimenьnik: "svět" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	worlds	świetach	světěh
noun - jimenьnik: "svět" | dative - měrьnik (komu? czemu?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	worlds	światom	světom
noun - jimenьnik: "svět" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	worlds	światami	světy
noun - jimenьnik: "svět" | vocative - zovateljь (o!) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	worlds	światy	světi
noun - jimenьnik: "vsehsvět" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	wszechświat	vsehsvět
noun - jimenьnik: "vsehsvět" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	wszechświat	vsehsvět
noun - jimenьnik: "vsehsvět" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	wszechświata	vsehsvěta
noun - jimenьnik: "vsehsvět" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	wszechświecie	vsehsvětě
noun - jimenьnik: "vsehsvět" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	wszechświatu/wszechświatowi	vsehsvětu
noun - jimenьnik: "vsehsvět" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	wszechświatem	vsehsvětomь
noun - jimenьnik: "vsehsvět" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	wszechświecie	vsehsvěte
noun - jimenьnik: "vsehsvět" | nominative - jimenovьnik (koto? čьto?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	wszechświaty	vsehsvěti
noun - jimenьnik: "vsehsvět" | accusative - vinьnik (kogo? čьto?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	wszechświaty	vsehsvěty
noun - jimenьnik: "vsehsvět" | genitive - rodilьnik (kogo? čego?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	wszechświatów	vsehsvět
noun - jimenьnik: "vsehsvět" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	wszechświetach	vsehsvětěh
noun - jimenьnik: "vsehsvět" | dative - měrьnik (komu? czemu?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	wszechświatom	vsehsvětom
noun - jimenьnik: "vsehsvět" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	wszechświatami	vsehsvěty
noun - jimenьnik: "vsehsvět" | vocative - zovateljь (o!) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	wszechświaty	vsehsvěti
noun - jimenьnik: "vsehsvět" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	uniwersum	vsehsvět
noun - jimenьnik: "vsehsvět" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	uniwersum	vsehsvět
noun - jimenьnik: "vsehsvět" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	uniwersum	vsehsvěta
noun - jimenьnik: "vsehsvět" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	uniwersum	vsehsvětě
noun - jimenьnik: "vsehsvět" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	uniwersum	vsehsvětu
noun - jimenьnik: "vsehsvět" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	uniwersum	vsehsvětomь
noun - jimenьnik: "vsehsvět" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universe	uniwersum	vsehsvěte
noun - jimenьnik: "vsehsvět" | nominative - jimenovьnik (koto? čьto?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	uniwersy	vsehsvěti
noun - jimenьnik: "vsehsvět" | accusative - vinьnik (kogo? čьto?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	uniwersy	vsehsvěty
noun - jimenьnik: "vsehsvět" | genitive - rodilьnik (kogo? čego?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	uniwersów	vsehsvět
noun - jimenьnik: "vsehsvět" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	uniwersach	vsehsvětěh
noun - jimenьnik: "vsehsvět" | dative - měrьnik (komu? czemu?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	uniwersom	vsehsvětom
noun - jimenьnik: "vsehsvět" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	uniwersami	vsehsvěty
noun - jimenьnik: "vsehsvět" | vocative - zovateljь (o!) | munoga ličьba - plural | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	universes	uniwersy	vsehsvěti
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dziura	dura
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dziurę	durǫ
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dziury	dury
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dziurze	durě
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dziurze	durě
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dziurą	durojǫ
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dziuro	duro
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dziury	dury
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dziury	dury
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dziur	dur
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dziurach	durah
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dziurom	duram
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dziurami	durami
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dziury	dury
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dura	dura
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	durę	durǫ
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	dury	dury
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	durze	durě
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	durze	durě
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	durą	durojǫ
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	hole	duro	duro
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dury	dury
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dury	dury
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dur	dur
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	durach	durah
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	durom	duram
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	durami	durami
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	holes	dury	dury
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small hole	dziurka	dura
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small hole	dziurkę	durǫ
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small hole	dziurki	dury
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small hole	dziurce	durě
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small hole	dziurce	durě
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small hole	dziurką	durojǫ
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small hole	dziurko	duro
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small holes	dziurki	dury
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small holes	dziurki	dury
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small holes	dziurek	dur
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small holes	dziurkach	durah
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small holes	dziurkom	duram
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small holes	dziurkami	durami
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	small holes	dziurki	dury
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny hole	dziureczka	dura
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny hole	dziureczkę	durǫ
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny hole	dziureczki	dury
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny hole	dziureczce	durě
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny hole	dziureczce	durě
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny hole	dziureczką	durojǫ
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny hole	dziureczko	duro
noun - jimenьnik: "dura" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny holes	dziureczki	dury
noun - jimenьnik: "dura" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny holes	dziureczki	dury
noun - jimenьnik: "dura" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny holes	dziureczek	dur
noun - jimenьnik: "dura" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny holes	dziureczkach	durah
noun - jimenьnik: "dura" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny holes	dziureczkom	duram
noun - jimenьnik: "dura" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny holes	dziureczkami	durami
noun - jimenьnik: "dura" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	tiny holes	dziureczki	dury
noun - jimenьnik: "napadьnik" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attacker	napadnik	napadьnik
noun - jimenьnik: "napadьnik" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attacker	napadnika	napadьnika
noun - jimenьnik: "napadьnik" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attacker	napadnika	napadьnika
noun - jimenьnik: "napadьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attacker	napadniku	napadьniku
noun - jimenьnik: "napadьnik" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attacker	napadnikowi	napadьniku
noun - jimenьnik: "napadьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attacker	napadnikiem	napadьnikomь
noun - jimenьnik: "napadьnik" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attacker	napadniku	napadьniče
noun - jimenьnik: "napadьnik" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attackers	napadnicy	napadьnici
noun - jimenьnik: "napadьnik" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attackers	napadników	napadьniky
noun - jimenьnik: "napadьnik" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attackers	napadników	napadьnik
noun - jimenьnik: "napadьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attackers	napadnikach	napadьnicěh
noun - jimenьnik: "napadьnik" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attackers	napadnikom	napadьnikom
noun - jimenьnik: "napadьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attackers	napadnikami	napadьniky
noun - jimenьnik: "napadьnik" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	attackers	napadnicy	napadьnici
noun - jimenьnik: "napadьnik" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailant	napastnik	napadьnik
noun - jimenьnik: "napadьnik" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailant	napastnika	napadьnika
noun - jimenьnik: "napadьnik" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailant	napastnika	napadьnika
noun - jimenьnik: "napadьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailant	napastniku	napadьniku
noun - jimenьnik: "napadьnik" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailant	napastnikowi	napadьniku
noun - jimenьnik: "napadьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailant	napastnikiem	napadьnikomь
noun - jimenьnik: "napadьnik" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailant	napastniku	napadьniče
noun - jimenьnik: "napadьnik" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailants	napastnicy	napadьnici
noun - jimenьnik: "napadьnik" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailants	napastników	napadьniky
noun - jimenьnik: "napadьnik" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailants	napastników	napadьnik
noun - jimenьnik: "napadьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailants	napastnikach	napadьnikah
noun - jimenьnik: "napadьnik" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailants	napastnikom	napadьnikom
noun - jimenьnik: "napadьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailants	napastnikami	napadьniky
noun - jimenьnik: "napadьnik" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	assailants	napastnicy	napadьnici
noun - jimenьnik: "napadьnik" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressor	agresor	napadьnik
noun - jimenьnik: "napadьnik" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressor	agresora	napadьnika
noun - jimenьnik: "napadьnik" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressor	agresora	napadьnika
noun - jimenьnik: "napadьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressor	agresorze	napadьniku
noun - jimenьnik: "napadьnik" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressor	agresorowi	napadьniku
noun - jimenьnik: "napadьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressor	agresorem	napadьnikomь
noun - jimenьnik: "napadьnik" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressor	agresorze	napadьniče
noun - jimenьnik: "napadьnik" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressors	agresorzy	napadьnici
noun - jimenьnik: "napadьnik" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressors	agresorów	napadьnici
noun - jimenьnik: "napadьnik" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressors	agresorów	napadьnik
noun - jimenьnik: "napadьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressors	agresorach	napadьnicěh
noun - jimenьnik: "napadьnik" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressors	agresorom	napadьnikom
noun - jimenьnik: "napadьnik" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressors	agresorami	napadьniky
noun - jimenьnik: "napadьnik" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	aggressors	agresorzy	napadьnici
noun - jimenьnik: "bornitelь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protector	protektor	borniteljь
noun - jimenьnik: "bornitelь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protector	protektora	bornitelja
noun - jimenьnik: "bornitelь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protector	protektora	bornitelja
noun - jimenьnik: "bornitelь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protector	protektorze	bornitelji
noun - jimenьnik: "bornitelь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protector	protektorowi	bornitelju
noun - jimenьnik: "bornitelь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protector	protektorem	borniteljemь
noun - jimenьnik: "bornitelь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protector	protektorze	bornitelju
noun - jimenьnik: "bornitelь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protectors	protektorzy	bornitelji
noun - jimenьnik: "bornitelь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protectors	protektorów	bornitelji
noun - jimenьnik: "bornitelь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protectors	protektorów	bornitelji
noun - jimenьnik: "bornitelь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protectors	protektorach	borniteljih
noun - jimenьnik: "bornitelь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protectors	protektorom	borniteljem
noun - jimenьnik: "bornitelь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protectors	protektorami	bornitelji
noun - jimenьnik: "bornitelь" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	protectors	protektorzy	bornitelji
noun - jimenьnik: "čistitelь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaner	czyściciel	čistiteljь
noun - jimenьnik: "čistitelь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaner	czyściciela	čistitelja
noun - jimenьnik: "čistitelь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaner	czyściciela	čistitelja
noun - jimenьnik: "čistitelь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaner	czyścicielu	čistitelji
noun - jimenьnik: "čistitelь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaner	czyścicielowi	čistitelju
noun - jimenьnik: "čistitelь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaner	czyścicielem	čistiteljemь
noun - jimenьnik: "čistitelь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaner	czyścicielu	čistitelju
noun - jimenьnik: "čistitelь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaners	czyściciele	čistitelji
noun - jimenьnik: "čistitelь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaners	czyścicieli	čistitelji
noun - jimenьnik: "čistitelь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaners	czyścicieli	čistitelji
noun - jimenьnik: "čistitelь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaners	czyścicielach	čistiteljih
noun - jimenьnik: "čistitelь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaners	czyścicielom	čistiteljem
noun - jimenьnik: "čistitelь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaners	czyścicielami	čistitelji
noun - jimenьnik: "čistitelь" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	cleaners	czyściciele	čistitelji
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przezroczystość	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przezroczystość	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przezroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przezroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przezroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przezroczystością	prozorčьnostьjǫ
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przezroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przezroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przezroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przezroczystości	prozorčьnostьji
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przezroczystościach	prozorčьnostih
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przezroczystościom	prozorčьnostim
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przezroczystościami	prozorčьnostьmi
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przezroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczność	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczność	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźrocznością	prozorčьnostьjǫ
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnostьji
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystościach	prozorčьnostih
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystościom	prozorčьnostim
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystościami	prozorčьnostьmi
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przejrzystość	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przejrzystość	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przejrzystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przejrzystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przejrzystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przejrzystością	prozorčьnostьjǫ
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przejrzystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przejrzystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przejrzystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przejrzystości	prozorčьnostьji
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przejrzystościach	prozorčьnostih
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przejrzystościom	prozorčьnostim
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przejrzystościami	prozorčьnostьmi
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przejrzystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczystość	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczystość	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczystością	prozorčьnostьjǫ
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnostьji
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystościach	prozorčьnostih
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystościom	prozorčьnostim
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystościami	prozorčьnostьmi
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	przeźroczystości	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	transparentność	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	transparentność	prozorčьnostь
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	transparentności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	transparentności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	transparentności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	transparentnością	prozorčьnostьjǫ
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparency, pellucidity, clarity, translucency, openness, limpidity, clearness, sheeriness, lucidity, visibility	transparentności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	transparentności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	transparentności	prozorčьnosti
noun - jimenьnik: "prozorčьnostь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	transparentności	prozorčьnostьji
noun - jimenьnik: "prozorčьnostь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	transparentnościach	prozorčьnostih
noun - jimenьnik: "prozorčьnostь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	transparentnościom	prozorčьnostim
noun - jimenьnik: "prozorčьnostь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	transparentnościami	prozorčьnostьmi
noun - jimenьnik: "prozorčьnostь" | vocative - zovateljь (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	transparencies, pellucidities, clarities, translucencies, opennesses, limpidities, clearnesses, sheerinesses, lucidities, visibilities	transparentności	prozorčьnosti
noun - jimenьnik: "zagorda" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corral, enclosure, croft, farm, farmyard, farmstead, courtyard, farmstead, homestead, paddock, livestock fold, outbuildings area	zagroda	zagorda
noun - jimenьnik: "zagorda" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corral, enclosure, croft, farm, farmyard, farmstead, courtyard, farmstead, homestead, paddock, livestock fold, outbuildings area	zagrody	zagordy
noun - jimenьnik: "zagorda" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corral, enclosure, croft, farm, farmyard, farmstead, courtyard, farmstead, homestead, paddock, livestock fold, outbuildings area	zagrodzie	zagordě
noun - jimenьnik: "zagorda" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corral, enclosure, croft, farm, farmyard, farmstead, courtyard, farmstead, homestead, paddock, livestock fold, outbuildings area	zagrodzie	zagordě
noun - jimenьnik: "zagorda" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corral, enclosure, croft, farm, farmyard, farmstead, courtyard, farmstead, homestead, paddock, livestock fold, outbuildings area	zagroda	zagorda
noun - jimenьnik: "zagorda" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corral, enclosure, croft, farm, farmyard, farmstead, courtyard, farmstead, homestead, paddock, livestock fold, outbuildings area	zagrodą	zagordojǫ
noun - jimenьnik: "zagorda" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corral, enclosure, croft, farm, farmyard, farmstead, courtyard, farmstead, homestead, paddock, livestock fold, outbuildings area	zagrodo	zagordo
noun - jimenьnik: "zagorda" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corrals, enclosures, crofts, farms, farmyards, farmsteads, courtyards, farmsteads, homesteads, paddocks, livestock folds, outbuildings areas	zagrody	zagordy
noun - jimenьnik: "zagorda" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corrals, enclosures, crofts, farms, farmyards, farmsteads, courtyards, farmsteads, homesteads, paddocks, livestock folds, outbuildings areas	zagrody	zagordy
noun - jimenьnik: "zagorda" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corrals, enclosures, crofts, farms, farmyards, farmsteads, courtyards, farmsteads, homesteads, paddocks, livestock folds, outbuildings areas	zagród	zagord
noun - jimenьnik: "zagorda" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corrals, enclosures, crofts, farms, farmyards, farmsteads, courtyards, farmsteads, homesteads, paddocks, livestock folds, outbuildings areas	zagrodach	zagordah
noun - jimenьnik: "zagorda" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corrals, enclosures, crofts, farms, farmyards, farmsteads, courtyards, farmsteads, homesteads, paddocks, livestock folds, outbuildings areas	zagrodom	zagordam
noun - jimenьnik: "zagorda" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corrals, enclosures, crofts, farms, farmyards, farmsteads, courtyards, farmsteads, homesteads, paddocks, livestock folds, outbuildings areas	zagrodami	zagordy
noun - jimenьnik: "zagorda" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	corrals, enclosures, crofts, farms, farmyards, farmsteads, courtyards, farmsteads, homesteads, paddocks, livestock folds, outbuildings areas	zagrody	zagordy
noun - jimenьnik: "duša" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	dusza	duša
noun - jimenьnik: "duša" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszę	dušǫ
noun - jimenьnik: "duša" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszy	duši
noun - jimenьnik: "duša" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszy	duši
noun - jimenьnik: "duša" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszy	duši
noun - jimenьnik: "duša" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszą	dušejǫ
noun - jimenьnik: "duša" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszo	duše
noun - jimenьnik: "duša" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusze	duše
noun - jimenьnik: "duša" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusze	duše
noun - jimenьnik: "duša" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusz	duš
noun - jimenьnik: "duša" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	duszach	dušah
noun - jimenьnik: "duša" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	duszom	dušam
noun - jimenьnik: "duša" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	duszami	dušami
noun - jimenьnik: "duša" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusze	duše
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianism, slavism	słowiaństwo	slověnьstvo
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianism, slavism	słowiaństwo	slověnьstvo
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianism, slavism	słowiaństwa	slověnьstva
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianism, slavism	słowiaństwie	slověnьstvě
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianism, slavism	słowiaństwu	slověnьstvu
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianism, slavism	słowiaństwem	slověnьstvomь
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianism, slavism	słowiaństwo	slověnьstvo
noun - jimenьnik: "ljudovoldьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianisms, slavisms	słowiaństwa	slověnьstva
noun - jimenьnik: "ljudovoldьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianisms, slavisms	słowiaństwa	slověnьstva
noun - jimenьnik: "ljudovoldьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianisms, slavisms	słowiaństw	slověnьstv
noun - jimenьnik: "ljudovoldьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianisms, slavisms	słowiaństwach	slověnьstvěh
noun - jimenьnik: "ljudovoldьstvo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianisms, slavisms	słowiaństwom	slověnьstvom
noun - jimenьnik: "ljudovoldьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianisms, slavisms	słowiaństwami	slověnьstvy
noun - jimenьnik: "ljudovoldьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	slovianisms, slavisms	słowiaństwa	slověnьstva
noun - jimenьnik: "holp" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasant	chłop	holp
noun - jimenьnik: "holp" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasant	chłopa	holpa
noun - jimenьnik: "holp" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasant	chłopa	holpa
noun - jimenьnik: "holp" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasant	chłopie	holpě
noun - jimenьnik: "holp" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasant	chłopowi	holpu
noun - jimenьnik: "holp" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasant	chłopem	holpom
noun - jimenьnik: "holp" | vocative - noun - jimenьnik: "holp" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasant	chłopie	holpe
noun - jimenьnik: "holp" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasants	chłopi/chłopy	holpi
noun - jimenьnik: "holp" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasants	chłopów	holpy
noun - jimenьnik: "holp" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasants	chłopów	holp
noun - jimenьnik: "holp" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasants	chłopach	holpěh
noun - jimenьnik: "holp" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasants	chłopom	holpom
noun - jimenьnik: "holp" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasants	chłopami	holpy
noun - jimenьnik: "holp" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	peasants	chłopi/chłopy	holpi
noun - jimenьnik: "porędok" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	order, tidiness	porządek	porędok
noun - jimenьnik: "porędok" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	order, tidiness	porządku	porędoka
noun - jimenьnik: "porędok" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	order, tidiness	porządkowi	porędoku
noun - jimenьnik: "porędok" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	order, tidiness	porządek	porędok
noun - jimenьnik: "porędok" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	order, tidiness	porządkiem	porędokomь
noun - jimenьnik: "porędok" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	order, tidiness	porządku	porędocě
noun - jimenьnik: "porędok" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	order, tidiness	porządku	porędoče
noun - jimenьnik: "porędok" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	orders, tidinesses	porządki	porędoci
noun - jimenьnik: "porędok" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	orders, tidinesses	porządki	porędoky
noun - jimenьnik: "porędok" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	orders, tidinesses	porządków	porędok
noun - jimenьnik: "porędok" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	orders, tidinesses	porządkach	porędocěh
noun - jimenьnik: "porędok" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	orders, tidinesses	porządkom	porędokom
noun - jimenьnik: "porędok" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	orders, tidinesses	porządkami	porędoky
noun - jimenьnik: "porędok" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	orders, tidinesses	porządki	porędoci
noun - jimenьnik: "gord" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	city, town, fortress	gród	gord
noun - jimenьnik: "gord" | accusative - vinьnik (kgo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	city, town, fortress	gród	gord
noun - jimenьnik: "gord" | genitive - rodilьnik (kgo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	city, town, fortress	gródu	gorda
noun - jimenьnik: "gord" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	city, town, fortress	grodzie	gordě
noun - jimenьnik: "gord" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	city, town, fortress	grodowi	gordu
noun - jimenьnik: "gord" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	city, town, fortress	grodem	gordomь
noun - jimenьnik: "gord" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	city, town, fortress	grodzie	gorde
noun - jimenьnik: "gord" | nominative - jimenovьnik (koto? čьto?) | plural - munga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cities, towns, fortresses	grody	gordi
noun - jimenьnik: "gord" | accusative - vinьnik (kgo? čьto?) | plural - munga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cities, towns, fortresses	grody	gordy
noun - jimenьnik: "gord" | genitive - rodilьnik (kgo? čego?) | plural - munga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cities, towns, fortresses	gródów	gord
noun - jimenьnik: "gord" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cities, towns, fortresses	gródach	gorděh
noun - jimenьnik: "gord" | dative - měrьnik (komu? čemu?) | plural - munga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cities, towns, fortresses	gródom	gordom
noun - jimenьnik: "gord" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cities, towns, fortresses	gródami	gordy
noun - jimenьnik: "gord" | vocative - zovanьnik (o!) | plural - munga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	cities, towns, fortresses	gródzie	gordi
noun - jimenьnik: "ličidlo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacus	liczydło	ličidlo
noun - jimenьnik: "ličidlo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacus	liczydło	ličidlo
noun - jimenьnik: "ličidlo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacus	liczydła	ličidla
noun - jimenьnik: "ličidlo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacus	liczydłe	ličidlě
noun - jimenьnik: "ličidlo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacus	liczydłu	ličidlu
noun - jimenьnik: "ličidlo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacus	liczydłem	ličidlomь
noun - jimenьnik: "ličidlo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacus	liczydło	ličidlo
noun - jimenьnik: "ličidlo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacuses	liczydła	ličidla
noun - jimenьnik: "ličidlo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacuses	liczydła	ličidla
noun - jimenьnik: "ličidlo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacuses	liczydeł	ličidl
noun - jimenьnik: "ličidlo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacuses	liczydłach	ličidlěh
noun - jimenьnik: "ličidlo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacuses	liczydłom	ličidlom
noun - jimenьnik: "ličidlo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacuses	liczydłami	ličidly
noun - jimenьnik: "ličidlo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	abacuses	liczydła	ličidla
noun - jimenьnik: "sulnice" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	sun	słońce	sulnice
noun - jimenьnik: "sulnice" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	sun	słońce	sulnice
noun - jimenьnik: "sulnice" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	sun	słońca	sulnica
noun - jimenьnik: "sulnice" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	sun	słońcu	sulnici
noun - jimenьnik: "sulnice" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	sun	słońcu	sulnicu
noun - jimenьnik: "sulnice" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	sun	słońcem	sulnicemь
noun - jimenьnik: "sulnice" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	sun	słońce	sulnice
noun - jimenьnik: "sulnice" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	suns	słońca	sulnica
noun - jimenьnik: "sulnice" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	suns	słońca	sulnica
noun - jimenьnik: "sulnice" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	suns	słońc	sulnic
noun - jimenьnik: "sulnice" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	suns	słońcach	sulnicih
noun - jimenьnik: "sulnice" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	suns	słońcom	sulnicem
noun - jimenьnik: "sulnice" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	suns	słońcami	sulnici
noun - jimenьnik: "sulnice" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	suns	słońca	sulnica
noun - jimenьnik: "gospodynji" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	lady, mistress	gospodyni	gospodynji
noun - jimenьnik: "gospodynji" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	lady, mistress	gospodynię	gospodynjǫ
noun - jimenьnik: "gospodynji" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	lady, mistress	gospodyni	gospodynje
noun - jimenьnik: "gospodynji" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	lady, mistress	gospodyni	gospodynji
noun - jimenьnik: "gospodynji" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	lady, mistress	gospodyni	gospodynji
noun - jimenьnik: "gospodynji" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	lady, mistress	gospodynią	gospodynjejǫ
noun - jimenьnik: "gospodynji" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	lady, mistress	gospodynio	gospodynje
noun - jimenьnik: "gospodynji" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	ladies, mistresses	gospodynie	gospodynje
noun - jimenьnik: "gospodynji" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	ladies, mistresses	gospodynie	gospodynje
noun - jimenьnik: "gospodynji" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	ladies, mistresses	gospodyń	gospodynjь
noun - jimenьnik: "gospodynji" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	ladies, mistresses	gospodyniach	gospodynjah
noun - jimenьnik: "gospodynji" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	ladies, mistresses	gospodyniom	gospodynjam
noun - jimenьnik: "gospodynji" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	ladies, mistresses	gospodyniami	gospodynjami
noun - jimenьnik: "gospodynji" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	ladies, mistresses	gospodynie	gospodynje
noun - jimenьnik: "konjь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horse	koń	konjь
noun - jimenьnik: "konjь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horse	konia	konja
noun - jimenьnik: "konjь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horse	konia	konja
noun - jimenьnik: "konjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horse	koniu	konji
noun - jimenьnik: "konjь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horse	koniowi/koniu	konju
noun - jimenьnik: "konjь" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horse	koniem	konjem
noun - jimenьnik: "konjь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horse	koniu	konju
noun - jimenьnik: "konjь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horses	konie	konji
noun - jimenьnik: "konjь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horses	konie	konje
noun - jimenьnik: "konjь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horses	koni	konji
noun - jimenьnik: "konjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horses	koniach	konjih
noun - jimenьnik: "konjь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horses	koniom	konjem
noun - jimenьnik: "konjь" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horses	koniami/końmi	konji
noun - jimenьnik: "konjь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	horses	konie	konji
noun - jimenьnik: "vodjь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leader, chief, commander, chieftain, head, warlord, ruler, skipper, boss, chieftainship, figurehead, duce	wódz	vodjь
noun - jimenьnik: "vodjь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leader, chief, commander, chieftain, head, warlord, ruler, skipper, boss, chieftainship, figurehead, duce	wodza	vodja
noun - jimenьnik: "vodjь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leader, chief, commander, chieftain, head, warlord, ruler, skipper, boss, chieftainship, figurehead, duce	wodza	vodja
noun - jimenьnik: "vodjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leader, chief, commander, chieftain, head, warlord, ruler, skipper, boss, chieftainship, figurehead, duce	wodzu	vodji
noun - jimenьnik: "vodjь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leader, chief, commander, chieftain, head, warlord, ruler, skipper, boss, chieftainship, figurehead, duce	wodzowi/wodzu	vodju
noun - jimenьnik: "vodjь" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leader, chief, commander, chieftain, head, warlord, ruler, skipper, boss, chieftainship, figurehead, duce	wodzem	vodjem
noun - jimenьnik: "vodjь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leader, chief, commander, chieftain, head, warlord, ruler, skipper, boss, chieftainship, figurehead, duce	wodzu	vodju
noun - jimenьnik: "vodjь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leaders, chiefs, commanders, chieftains, heads, warlords, rulers, skippers, bosses, chieftainships, figureheads, duces	wodzowie	vodji
noun - jimenьnik: "vodjь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leaders, chiefs, commanders, chieftains, heads, warlords, rulers, skippers, bosses, chieftainships, figureheads, duces	wodzów	vodje
noun - jimenьnik: "vodjь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leaders, chiefs, commanders, chieftains, heads, warlords, rulers, skippers, bosses, chieftainships, figureheads, duces	wodzów	vodji
noun - jimenьnik: "vodjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leaders, chiefs, commanders, chieftains, heads, warlords, rulers, skippers, bosses, chieftainships, figureheads, duces	wodzach	vodjih
noun - jimenьnik: "vodjь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leaders, chiefs, commanders, chieftains, heads, warlords, rulers, skippers, bosses, chieftainships, figureheads, duces	wodzom	vodjem
noun - jimenьnik: "vodjь" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leaders, chiefs, commanders, chieftains, heads, warlords, rulers, skippers, bosses, chieftainships, figureheads, duces	wodzami	vodji
noun - jimenьnik: "vodjь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	leaders, chiefs, commanders, chieftains, heads, warlords, rulers, skippers, bosses, chieftainships, figureheads, duces	wodzowie	vodji
noun - jimenьnik: "gospodь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentleman, mr, sir, lord	pan	gospodь
noun - jimenьnik: "gospodь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentleman, mr, sir, lord	pana	gospodi
noun - jimenьnik: "gospodь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentleman, mr, sir, lord	pana	gospodi
noun - jimenьnik: "gospodь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentleman, mr, sir, lord	panie	gospodi
noun - jimenьnik: "gospodь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentleman, mr, sir, lord	panu	gospodi
noun - jimenьnik: "gospodь" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentleman, mr, sir, lord	panem	gospodim
noun - jimenьnik: "gospodь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentleman, mr, sir, lord	panie	gospodi
noun - jimenьnik: "gospodь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentlemen, messrs, sirs, lords	panowie	gospodje
noun - jimenьnik: "gospodь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentlemen, messrs, sirs, lords	panów	gospodi
noun - jimenьnik: "gospodь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentlemen, messrs, sirs, lords	panów	gospodьji
noun - jimenьnik: "gospodь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentlemen, messrs, sirs, lords	panach	gospodih
noun - jimenьnik: "gospodь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentlemen, messrs, sirs, lords	panom	gospodim
noun - jimenьnik: "gospodь" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentlemen, messrs, sirs, lords	panami	gospodьmi
noun - jimenьnik: "gospodь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gentlemen, messrs, sirs, lords	panowie	gospodje
noun - jimenьnik: "zork" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	wzrok	zork
noun - jimenьnik: "zork" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	wzrok	zork
noun - jimenьnik: "zork" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	wzroku	zorka
noun - jimenьnik: "zork" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	wzroku	zorcě
noun - jimenьnik: "zork" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	wzrokowi	zorku
noun - jimenьnik: "zork" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	wzrokiem	zorkomь
noun - jimenьnik: "zork" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zroku	zorče
noun - jimenьnik: "zork" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	wzroki	zorci
noun - jimenьnik: "zork" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	wzroki	zorky
noun - jimenьnik: "zork" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	wzroków	zork
noun - jimenьnik: "zork" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	wzrokach	zorcěh
noun - jimenьnik: "zork" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	wzrokom	zorkom
noun - jimenьnik: "zork" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	wzrokami	zorky
noun - jimenьnik: "zork" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	wzroki	zorci
noun - jimenьnik: "zork" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zrok	zork
noun - jimenьnik: "zork" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zrok	zork
noun - jimenьnik: "zork" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zroku	zorka
noun - jimenьnik: "zork" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zroku	zorku
noun - jimenьnik: "zork" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zrokowi	zorku
noun - jimenьnik: "zork" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zrokiem	zorkomь
noun - jimenьnik: "zork" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sight (ability to see), eyesight	zroku	zorče
noun - jimenьnik: "zork" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	zroki	zorci
noun - jimenьnik: "zork" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	zroki	zorky
noun - jimenьnik: "zork" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	zroków	zork
noun - jimenьnik: "zork" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	zrokach	zorcěh
noun - jimenьnik: "zork" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	zrokom	zorkom
noun - jimenьnik: "zork" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	zrokami	zorky
noun - jimenьnik: "zork" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	sights (abilities to see), eyesights	zroki	zorci
noun - jimenьnik: "vid" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wizja	vid
noun - jimenьnik: "vid" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wizję	vid
noun - jimenьnik: "vid" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wizji	vida
noun - jimenьnik: "vid" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wizji	vidě
noun - jimenьnik: "vid" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wizji	vidu
noun - jimenьnik: "vid" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wizją	vidomь
noun - jimenьnik: "vid" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wizjo	vide
noun - jimenьnik: "vid" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	wizje	vidi
noun - jimenьnik: "vid" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	wizje	vidy
noun - jimenьnik: "vid" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	wizji	vid
noun - jimenьnik: "vid" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	wizjach	viděh
noun - jimenьnik: "vid" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	wizjem	vidom
noun - jimenьnik: "vid" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	wizjami	vidy
noun - jimenьnik: "vid" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	wizje	vidi
noun - jimenьnik: "vid" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wid	vid
noun - jimenьnik: "vid" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wid	vid
noun - jimenьnik: "vid" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	wida	vida
noun - jimenьnik: "vid" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	widzie	vidě
noun - jimenьnik: "vid" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	widowi	vidu
noun - jimenьnik: "vid" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	widem	vidomь
noun - jimenьnik: "vid" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	vision	widzie	vide
noun - jimenьnik: "vid" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	widy	vidi
noun - jimenьnik: "vid" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	widy	vidy
noun - jimenьnik: "vid" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	widów	vid
noun - jimenьnik: "vid" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	widach	viděh
noun - jimenьnik: "vid" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	widom	vidom
noun - jimenьnik: "vid" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	widami	vidy
noun - jimenьnik: "vid" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	visions	widy	vidi
noun - jimenьnik: "strojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	ustrój	strojь
noun - jimenьnik: "strojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	ustrój	strojь
noun - jimenьnik: "strojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	ustroju	stroja
noun - jimenьnik: "strojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	ustroju	stroji
noun - jimenьnik: "strojь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	ustrojowi/ustroju	stroju
noun - jimenьnik: "strojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	ustrojem	strojemь
noun - jimenьnik: "strojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	ustroju	stroju
noun - jimenьnik: "strojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	ustroje	stroji
noun - jimenьnik: "strojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	ustroje	stroje
noun - jimenьnik: "strojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	ustrojów/ustroi	stroji
noun - jimenьnik: "strojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	ustrojach	strojih
noun - jimenьnik: "strojь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	ustrojom	strojem
noun - jimenьnik: "strojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	ustrojami	stroji
noun - jimenьnik: "strojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	ustroje	stroji
noun - jimenьnik: "strojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	organizacja	strojь
noun - jimenьnik: "strojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	organizację	strojь
noun - jimenьnik: "strojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	organizacji	stroja
noun - jimenьnik: "strojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	organizacji	stroji
noun - jimenьnik: "strojь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	organizacji	stroju
noun - jimenьnik: "strojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	organizacją	strojemь
noun - jimenьnik: "strojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	organizacjo	stroju
noun - jimenьnik: "strojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	organizacje	stroji
noun - jimenьnik: "strojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	organizacje	stroje
noun - jimenьnik: "strojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	organizacji	stroji
noun - jimenьnik: "strojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	organizacjach	strojih
noun - jimenьnik: "strojь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	organizacjom	strojem
noun - jimenьnik: "strojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	organizacjami	stroji
noun - jimenьnik: "strojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	organizacje	stroji
noun - jimenьnik: "strojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	system	strojь
noun - jimenьnik: "strojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	system	strojь
noun - jimenьnik: "strojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	systemu	stroja
noun - jimenьnik: "strojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	systemie	stroji
noun - jimenьnik: "strojь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	systemowi/systemu	stroju
noun - jimenьnik: "strojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	systemem	strojemь
noun - jimenьnik: "strojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	system, organization, political system	systemie	stroju
noun - jimenьnik: "strojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	systemy	stroji
noun - jimenьnik: "strojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	systemy	stroje
noun - jimenьnik: "strojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	systemów	stroji
noun - jimenьnik: "strojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	systemach	strojih
noun - jimenьnik: "strojь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	systemom	strojem
noun - jimenьnik: "strojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	systemami	stroji
noun - jimenьnik: "strojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	systems, organizations, political systems, frameworks, regimes	systemy	stroji
noun - jimenьnik: "hata" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chata	hata
noun - jimenьnik: "hata" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chaty	haty
noun - jimenьnik: "hata" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chacie	hatě
noun - jimenьnik: "hata" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chacie	hatě
noun - jimenьnik: "hata" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chata	hata
noun - jimenьnik: "hata" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatą	hatojǫ
noun - jimenьnik: "hata" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chato	hato
noun - jimenьnik: "hata" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chaty	haty
noun - jimenьnik: "hata" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chaty	haty
noun - jimenьnik: "hata" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chat	hat
noun - jimenьnik: "hata" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatach	hatah
noun - jimenьnik: "hata" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatom	hatam
noun - jimenьnik: "hata" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatami	hatami
noun - jimenьnik: "hata" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chaty	haty
noun - jimenьnik: "hata" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatka	hata
noun - jimenьnik: "hata" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatkę	hatǫ
noun - jimenьnik: "hata" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatki	haty
noun - jimenьnik: "hata" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatce	hatě
noun - jimenьnik: "hata" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatce	hata
noun - jimenьnik: "hata" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatką	hatojǫ
noun - jimenьnik: "hata" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottage, cabin, hut, shack, shanty, lodge, chalet, cabin, small cottage, little hut, tiny cabin, cozy cabin	chatko	hato
noun - jimenьnik: "hata" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatki	haty
noun - jimenьnik: "hata" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatki	haty
noun - jimenьnik: "hata" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatek	hat
noun - jimenьnik: "hata" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatkach	hatah
noun - jimenьnik: "hata" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatkom	hatam
noun - jimenьnik: "hata" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatkami	haty
noun - jimenьnik: "hata" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cottages, cabins, huts, shacks, shanties, lodges, chalets, cabins, small cottages, little huts, tiny cabins, cozy cabins	chatki	haty
noun - jimenьnik: "ognjь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fire	ogień	ognjь
noun - jimenьnik: "ognjь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fire	ognia	ognja
noun - jimenьnik: "ognjь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fire	ognia	ognja
noun - jimenьnik: "ognjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fire	ogniu	ognji
noun - jimenьnik: "ognjь" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fire	ogniu/ogniowi	ognju
noun - jimenьnik: "ognjь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fire	ogniem	ognjemь
noun - jimenьnik: "ognjь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fire	ogniu	ognju
noun - jimenьnik: "ognjь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fires	ognie	ognji
noun - jimenьnik: "ognjь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fires	ognie	ognje
noun - jimenьnik: "ognjь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fires	ogni/ogniów	ognji
noun - jimenьnik: "ognjь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fires	ogniach	ognjih
noun - jimenьnik: "ognjь" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fires	ogniom	ognjem
noun - jimenьnik: "ognjь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fires	ogniami	ognji
noun - jimenьnik: "ognjь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	fires	ognie	ognji
noun - jimenьnik: "nastrojь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humor	humor	nastrojь
noun - jimenьnik: "nastrojь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humor	humor	nastrojь
noun - jimenьnik: "nastrojь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humor	humoru	nastroji
noun - jimenьnik: "nastrojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humor	humorze	nastroji
noun - jimenьnik: "nastrojь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humor	humorowi	nastroju
noun - jimenьnik: "nastrojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humor	humorem	nastrojemь
noun - jimenьnik: "nastrojь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humor	humorze	nastroji
noun - jimenьnik: "nastrojь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humors	humory	nastroji
noun - jimenьnik: "nastrojь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humors	humory	nastroje
noun - jimenьnik: "nastrojь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humors	humorów	nastroji
noun - jimenьnik: "nastrojь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humors	humorach	nastrojih
noun - jimenьnik: "nastrojь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humors	humorom	nastrojem
noun - jimenьnik: "nastrojь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humors	humorami	nastroji
noun - jimenьnik: "nastrojь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	humors	humory	nastroji
noun - jimenьnik: "ljud" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnos	etnos	ljud
noun - jimenьnik: "ljud" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnos	etnos	ljud
noun - jimenьnik: "ljud" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnos	etnosu	ljuda
noun - jimenьnik: "ljud" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnos	etnosie	ljudě
noun - jimenьnik: "ljud" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnos	etnosowi	ljudu
noun - jimenьnik: "ljud" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnos	etnosem	ljudomь
noun - jimenьnik: "ljud" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnos	etnosie	ljude
noun - jimenьnik: "ljud" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnoses	etnosy	ljudi
noun - jimenьnik: "ljud" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnoses	etnosy	ljudy
noun - jimenьnik: "ljud" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnoses	etnosów	ljud
noun - jimenьnik: "ljud" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnoses	etnosach	ljuděh
noun - jimenьnik: "ljud" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnoses	etnosom	ljudom
noun - jimenьnik: "ljud" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnoses	etnosami	ljudy
noun - jimenьnik: "ljud" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	ethnoses	etnosy	ljudi
noun - jimenьnik: "juděnьje" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	inciting, instigating, provoking, stirring the pot, agitating, egging on, sowing discord, pitting against, fomenting, goading	judzenie	juděnьje
noun - jimenьnik: "juděnьje" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	inciting, instigating, provoking, stirring the pot, agitating, egging on, sowing discord, pitting against, fomenting, goading	judzenie	juděnьje
noun - jimenьnik: "juděnьje" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	inciting, instigating, provoking, stirring the pot, agitating, egging on, sowing discord, pitting against, fomenting, goading	judzenia	juděnьja
noun - jimenьnik: "juděnьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	inciting, instigating, provoking, stirring the pot, agitating, egging on, sowing discord, pitting against, fomenting, goading	judzeniu	juděnьji
noun - jimenьnik: "juděnьje" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	inciting, instigating, provoking, stirring the pot, agitating, egging on, sowing discord, pitting against, fomenting, goading	judzeniu	juděnьju
noun - jimenьnik: "juděnьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	inciting, instigating, provoking, stirring the pot, agitating, egging on, sowing discord, pitting against, fomenting, goading	judzeniem	juděnьjemь
noun - jimenьnik: "juděnьje" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	inciting, instigating, provoking, stirring the pot, agitating, egging on, sowing discord, pitting against, fomenting, goading	judzenie	juděnьje
noun - jimenьnik: "juděnьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incitings, instigatings, provokings, stirrings the pot, agitatings, eggings on, sowings discord, pittings against, fomentings, goadings	judzenia	juděnьja
noun - jimenьnik: "juděnьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incitings, instigatings, provokings, stirrings the pot, agitatings, eggings on, sowings discord, pittings against, fomentings, goadings	judzenia	juděnьja
noun - jimenьnik: "juděnьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incitings, instigatings, provokings, stirrings the pot, agitatings, eggings on, sowings discord, pittings against, fomentings, goadings	judzeń	juděnij
noun - jimenьnik: "juděnьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incitings, instigatings, provokings, stirrings the pot, agitatings, eggings on, sowings discord, pittings against, fomentings, goadings	judzeniach	juděnьjih
noun - jimenьnik: "juděnьje" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incitings, instigatings, provokings, stirrings the pot, agitatings, eggings on, sowings discord, pittings against, fomentings, goadings	judzeniom	juděnьjem
noun - jimenьnik: "juděnьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incitings, instigatings, provokings, stirrings the pot, agitatings, eggings on, sowings discord, pittings against, fomentings, goadings	judzeniami	juděnьji
noun - jimenьnik: "juděnьje" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	incitings, instigatings, provokings, stirrings the pot, agitatings, eggings on, sowings discord, pittings against, fomentings, goadings	judzenia	juděnьja
noun - jimenьnik: "suhod" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircase, step (single stair of a staircase)	schód	suhod
noun - jimenьnik: "suhod" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircase, step (single stair of a staircase)	schód	suhod
noun - jimenьnik: "suhod" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircase, step (single stair of a staircase)	schodu	suhoda
noun - jimenьnik: "suhod" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircase, step (single stair of a staircase)	schodzie	suhodě
noun - jimenьnik: "suhod" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircase, step (single stair of a staircase)	schodowi	suhodu
noun - jimenьnik: "suhod" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircase, step (single stair of a staircase)	schodem	suhodomь
noun - jimenьnik: "suhod" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircase, step (single stair of a staircase)	schodzie	suhode
noun - jimenьnik: "suhod" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircases, steps (single stairs of a staircase)	schody	suhody
noun - jimenьnik: "suhod" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircases, steps (single stairs of a staircase)	schody	suhodi
noun - jimenьnik: "suhod" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircases, steps (single stairs of a staircase)	schodów	suhod
noun - jimenьnik: "suhod" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircases, steps (single stairs of a staircase)	schodom	suhodom
noun - jimenьnik: "suhod" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircases, steps (single stairs of a staircase)	schodach	suhoděh
noun - jimenьnik: "suhod" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircases, steps (single stairs of a staircase)	schodami	suhody
noun - jimenьnik: "suhod" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	staircases, steps (single stairs of a staircase)	schody	suhodi
noun - jimenьnik: "čelověčenьstvo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwo	čelověčenьstvo
noun - jimenьnik: "čelověčenьstvo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwo	čelověčenьstvo
noun - jimenьnik: "čelověčenьstvo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwa	čelověčenьstva
noun - jimenьnik: "čelověčenьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwie	čelověčenьstvě
noun - jimenьnik: "čelověčenьstvo" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwu	čelověčenьstvu
noun - jimenьnik: "čelověčenьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwem	čelověčenьstvomь
noun - jimenьnik: "čelověčenьstvo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwo	čelověčenьstvo
noun - jimenьnik: "čelověčenьstvo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwa	čelověčenьstva
noun - jimenьnik: "čelověčenьstvo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwa	čelověčenьstva
noun - jimenьnik: "čelověčenьstvo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństw	čelověčenьstv
noun - jimenьnik: "čelověčenьstvo" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwach	čelověčenьstvěh
noun - jimenьnik: "čelověčenьstvo" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwom	čelověčenьstvom
noun - jimenьnik: "čelověčenьstvo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwami	čelověčenьstvy
noun - jimenьnik: "čelověčenьstvo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	humanity	człowieczeństwa	čelověčenьstva
noun - jimenьnik: "nǫdja" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymus	nǫdja
noun - jimenьnik: "nǫdja" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymus	nǫdjǫ
noun - jimenьnik: "nǫdja" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusu	nǫdje
noun - jimenьnik: "nǫdja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusie	nǫdji
noun - jimenьnik: "nǫdja" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusowi	nǫdji
noun - jimenьnik: "nǫdja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusem	nǫdějǫ
noun - jimenьnik: "nǫdja" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusie	nǫdje
noun - jimenьnik: "nǫdja" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusy	nǫdje
noun - jimenьnik: "nǫdja" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusy	nǫdje
noun - jimenьnik: "nǫdja" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusów	nǫdjь
noun - jimenьnik: "nǫdja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusach	nǫdjah
noun - jimenьnik: "nǫdja" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusom	nǫdjam
noun - jimenьnik: "nǫdja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusami	nǫdjami
noun - jimenьnik: "nǫdja" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	duress	przymusy	nǫdje
noun - jimenьnik: "obraza" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insult, affront	obraza	obraza
noun - jimenьnik: "obraza" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insult, affront	obrazę	obrazǫ
noun - jimenьnik: "obraza" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insult, affront	obrazy	obrazy
noun - jimenьnik: "obraza" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insult, affront	obrazie	obrazě
noun - jimenьnik: "obraza" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insult, affront	obrazą	obrazejǫ
noun - jimenьnik: "obraza" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insult, affront	obrazie	obrazě
noun - jimenьnik: "obraza" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insult, affront	obrazo	obraze
noun - jimenьnik: "obraza" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insults, affronts	obrazy	obrazy
noun - jimenьnik: "obraza" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insults, affronts	obrazy	obrazy
noun - jimenьnik: "obraza" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insults, affronts	obraz	obraz
noun - jimenьnik: "obraza" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insults, affronts	obrazom	obrazam
noun - jimenьnik: "obraza" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insults, affronts	obrazami	obrazami
noun - jimenьnik: "obraza" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insults, affronts	obrazach	obrazah
noun - jimenьnik: "obraza" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	insults, affronts	obrazy	obrazy
noun - jimenьnik: "věda" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-how	wiedza	věda
noun - jimenьnik: "věda" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-how	wiedzę	vědǫ
noun - jimenьnik: "věda" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-how	wiedzy	vědy
noun - jimenьnik: "věda" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-how	wiedzy	vědě
noun - jimenьnik: "věda" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-how	wiedzy	vědě
noun - jimenьnik: "věda" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-how	wiedzą	vědojǫ
noun - jimenьnik: "věda" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-how	wiedzo	vědo
noun - jimenьnik: "věda" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-hows	wiedze	vědy
noun - jimenьnik: "věda" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-hows	wiedze	vědy
noun - jimenьnik: "věda" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-hows	wiedz	věd
noun - jimenьnik: "věda" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-hows	wiedzach	vědah
noun - jimenьnik: "věda" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-hows	wiedzom	vědam
noun - jimenьnik: "věda" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-hows	wiedzami	vědami
noun - jimenьnik: "věda" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	knowledge, know-hows	wiedze	vědy
noun - jimenьnik: "edьnota" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unity	jednota	edьnota
noun - jimenьnik: "edьnota" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unity	jednotę	edьnotǫ
noun - jimenьnik: "edьnota" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unity	jednoty	edьnoty
noun - jimenьnik: "edьnota" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unity	jednocie	edьnotě
noun - jimenьnik: "edьnota" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unity	jednocie	edьnotě
noun - jimenьnik: "edьnota" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unity	jednotą	edьnotojǫ
noun - jimenьnik: "edьnota" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unity	jednoto	edьnoto
noun - jimenьnik: "edьnota" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unities	jednoty	edьnoty
noun - jimenьnik: "edьnota" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unities	jednoty	edьnoty
noun - jimenьnik: "edьnota" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unities	jednot	edьnot
noun - jimenьnik: "edьnota" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unities	jednotach	edьnotah
noun - jimenьnik: "edьnota" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unities	jednotom	edьnotam
noun - jimenьnik: "edьnota" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unities	jednotami	edьnoty
noun - jimenьnik: "edьnota" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	unities	jednoty	edьnoty
noun - jimenьnik: "tьpun" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpun	tьpun
noun - jimenьnik: "tьpun" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpuna	tьpuna
noun - jimenьnik: "tьpun" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpuna	tьpuna
noun - jimenьnik: "tьpun" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunie	tьpuně
noun - jimenьnik: "tьpun" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunowi	tьpunu
noun - jimenьnik: "tьpun" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunem	tьpunomь
noun - jimenьnik: "tьpun" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunie	tьpune
noun - jimenьnik: "tьpun" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpuni	tьpuni
noun - jimenьnik: "tьpun" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunów	tьpuny
noun - jimenьnik: "tьpun" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunów	tьpun
noun - jimenьnik: "tьpun" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunach	tьpuněh
noun - jimenьnik: "tьpun" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunom	tьpunom
noun - jimenьnik: "tьpun" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpunami	tьpuny
noun - jimenьnik: "tьpun" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	drug addict, alcoholic	ćpuni	tьpuni
noun - jimenьnik: "běgun" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runner (person or animal who runs fast)	biegun	běgun
noun - jimenьnik: "běgun" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runner (person or animal who runs fast)	bieguna	běguna
noun - jimenьnik: "běgun" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runner (person or animal who runs fast)	bieguna	běguna
noun - jimenьnik: "běgun" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runner (person or animal who runs fast)	biegunie	běguně
noun - jimenьnik: "běgun" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runner (person or animal who runs fast)	biegunowi	běgunu
noun - jimenьnik: "běgun" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runner (person or animal who runs fast)	biegunem	běgunom
noun - jimenьnik: "běgun" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runner (person or animal who runs fast)	biegunie	běgune
noun - jimenьnik: "běgun" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runners (persons or animals who run fast)	bieguni	běguni
noun - jimenьnik: "běgun" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runners (persons or animals who run fast)	biegunów	běguny
noun - jimenьnik: "běgun" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runners (persons or animals who run fast)	biegunów	běgun
noun - jimenьnik: "běgun" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runners (persons or animals who run fast)	biegunach	běguněh
noun - jimenьnik: "běgun" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runners (persons or animals who run fast)	biegunom	běgunom
noun - jimenьnik: "běgun" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runners (persons or animals who run fast)	biegunami	běguny
noun - jimenьnik: "běgun" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	runners (persons or animals who run fast)	bieguni	běguni
noun - jimenьnik: "běgun" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witcher	wiedun	vědun
noun - jimenьnik: "běgun" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witcher	wieduna	věduna
noun - jimenьnik: "běgun" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witcher	wieduna	věduna
noun - jimenьnik: "běgun" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witcher	wiedunie	věduně
noun - jimenьnik: "běgun" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witcher	wiedunowi	vědunu
noun - jimenьnik: "běgun" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witcher	wiedunem	vědunomь
noun - jimenьnik: "běgun" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witcher	wiedunie	vědune
noun - jimenьnik: "běgun" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witchers	wieduni	věduni
noun - jimenьnik: "běgun" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witchers	wiedunów	věduny
noun - jimenьnik: "běgun" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witchers	wiedunów	vědun
noun - jimenьnik: "běgun" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witchers	wiedunach	věduněh
noun - jimenьnik: "běgun" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witchers	wiedunom	vědunom
noun - jimenьnik: "běgun" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witchers	wiedunami	věduny
noun - jimenьnik: "běgun" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	witchers	wieduni	věduni
noun - jimenьnik: "pěhur" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) an infantryman	piechur	pěhur
noun - jimenьnik: "pěhur" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) an infantryman	piechura	pěhura
noun - jimenьnik: "pěhur" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) an infantryman	piechura	pěhura
noun - jimenьnik: "pěhur" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) an infantryman	piechurze	pěhurě
noun - jimenьnik: "pěhur" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) an infantryman	piechurowi/piechuru	pěhuru
noun - jimenьnik: "pěhur" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) an infantryman	piechurem	pěhuromь
noun - jimenьnik: "pěhur" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) an infantryman	piechurze	pěhure
noun - jimenьnik: "pěhur" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) infantrymen	piechurzy/piechury	pěhuri
noun - jimenьnik: "pěhur" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) infantrymen	piechurów	pěhury
noun - jimenьnik: "pěhur" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) infantrymen	piechurów	pěhur
noun - jimenьnik: "pěhur" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) infantrymen	piechurach	pěhurěh
noun - jimenьnik: "pěhur" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) infantrymen	piechurom	pěhurom
noun - jimenьnik: "pěhur" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) infantrymen	piechurami	pěhury
noun - jimenьnik: "pěhur" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	(military) infantrymen	piechurzy/piechury	pěhuri
noun - jimenьnik: "slověnьščina" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianland, slavicland, state of the slovians/slavs	słowiańszczyzna	slověnьščina
noun - jimenьnik: "slověnьščina" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianland, slavicland, state of the slovians/slavs	słowiańszczyznę	slověnьščinǫ
noun - jimenьnik: "slověnьščina" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianland, slavicland, state of the slovians/slavs	słowiańszczyzny	slověnьščiny
noun - jimenьnik: "slověnьščina" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianland, slavicland, state of the slovians/slavs	słowiańszczyźnie	slověnьščině
noun - jimenьnik: "slověnьščina" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianland, slavicland, state of the slovians/slavs	słowiańszczyźnie	slověnьščině
noun - jimenьnik: "slověnьščina" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianland, slavicland, state of the slovians/slavs	słowiańszczyzną	slověnьščinojǫ
noun - jimenьnik: "slověnьščina" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianland, slavicland, state of the slovians/slavs	słowiańszczyzno	slověnьščino
noun - jimenьnik: "slověnьščina" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianlands, slaviclands, states of the slovians/slavs	słowiańszczyzny	slověnьščiny
noun - jimenьnik: "slověnьščina" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianlands, slaviclands, states of the slovians/slavs	słowiańszczyzny	slověnьščiny
noun - jimenьnik: "slověnьščina" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianlands, slaviclands, states of the slovians/slavs	słowiańszczyzn	slověnьščin
noun - jimenьnik: "slověnьščina" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianlands, slaviclands, states of the slovians/slavs	słowiańszczyznach	slověnьščinah
noun - jimenьnik: "slověnьščina" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianlands, slaviclands, states of the slovians/slavs	słowiańszczyznom	slověnьščinam
noun - jimenьnik: "slověnьščina" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianlands, slaviclands, states of the slovians/slavs	słowiańszczyznami	slověnьščiny
noun - jimenьnik: "slověnьščina" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	slovianlands, slaviclands, states of the slovians/slavs	słowiańszczyzny	slověnьščiny
noun - jimenьnik: "žglišče" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	zgliszcze	žglišče
noun - jimenьnik: "žglišče" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	zgliszcze	žglišče
noun - jimenьnik: "žglišče" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	zgliszcza	žglišča
noun - jimenьnik: "žglišče" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	zgliszczu	žglišči
noun - jimenьnik: "žglišče" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	zgliszczu	žglišču
noun - jimenьnik: "žglišče" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	zgliszczem	žgliščemь
noun - jimenьnik: "žglišče" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	zgliszcze	žglišče
noun - jimenьnik: "žglišče" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	zgliszcza	žglišča
noun - jimenьnik: "žglišče" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	zgliszcza	žglišča
noun - jimenьnik: "žglišče" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	zgliszcz/zgliszczy	žgliščь
noun - jimenьnik: "žglišče" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	zgliszczach	žgliščih
noun - jimenьnik: "žglišče" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	zgliszczom	žgliščem
noun - jimenьnik: "žglišče" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	zgliszczami	žglišči
noun - jimenьnik: "žglišče" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	zgliszcza	žglišča
noun - jimenьnik: "žglišče" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	żgliszcze	žglišče
noun - jimenьnik: "žglišče" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	żgliszcze	žglišče
noun - jimenьnik: "žglišče" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	żgliszcza	žglišča
noun - jimenьnik: "žglišče" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	żgliszczu	žglišči
noun - jimenьnik: "žglišče" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	żgliszczu	žglišču
noun - jimenьnik: "žglišče" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	żgliszczem	žgliščemь
noun - jimenьnik: "žglišče" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruin	żgliszcze	žglišče
noun - jimenьnik: "žglišče" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	żgliszcza	žglišča
noun - jimenьnik: "žglišče" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	żgliszcza	žglišča
noun - jimenьnik: "žglišče" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	żgliszcz/żgliszczy	žgliščь
noun - jimenьnik: "žglišče" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	żgliszczach	žgliščih
noun - jimenьnik: "žglišče" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	żgliszczom	žgliščem
noun - jimenьnik: "žglišče" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	żgliszczami	žglišči
noun - jimenьnik: "žglišče" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	ruins	żgliszcza	žglišča
noun - jimenьnik: "višьnja" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherry	wiśnia	višьnja
noun - jimenьnik: "višьnja" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherry	wiśnię	višьnjǫ
noun - jimenьnik: "višьnja" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherry	wiśni	višьnje
noun - jimenьnik: "višьnja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherry	wiśni	višьnji
noun - jimenьnik: "višьnja" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherry	wiśni	višьnji
noun - jimenьnik: "višьnja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherry	wiśnią	višьnjejǫ
noun - jimenьnik: "višьnja" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherry	wiśnio	višьnje
noun - jimenьnik: "višьnja" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherries	wiśnie	višьnje
noun - jimenьnik: "višьnja" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherries	wiśnie	višьnje
noun - jimenьnik: "višьnja" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherries	wiśni	višьnji
noun - jimenьnik: "višьnja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherries	wiśniach	višьnjah
noun - jimenьnik: "višьnja" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherries	wiśniom	višьnjam
noun - jimenьnik: "višьnja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherries	wiśniami	višьnjami
noun - jimenьnik: "višьnja" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	cherries	wiśnie	višьnje
noun - jimenьnik: "pekarьnja" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakery, bakehouse, baking room	piekarnia	pekarьnja
noun - jimenьnik: "pekarьnja" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakery, bakehouse, baking room	piekarnię	pekarьnjǫ
noun - jimenьnik: "pekarьnja" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakery, bakehouse, baking room	piekarni	pekarьnje
noun - jimenьnik: "pekarьnja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakery, bakehouse, baking room	piekarni	pekarьnji
noun - jimenьnik: "pekarьnja" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakery, bakehouse, baking room	piekarni	pekarьnji
noun - jimenьnik: "pekarьnja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakery, bakehouse, baking room	piekarnią	pekarьnjejǫ
noun - jimenьnik: "pekarьnja" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakery, bakehouse, baking room	piekarnio	pekarьnje
noun - jimenьnik: "pekarьnja" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakeries, bakehouses, baking rooms	piekarnie	pekarьnje
noun - jimenьnik: "pekarьnja" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakeries, bakehouses, baking rooms	piekarnie	pekarьnje
noun - jimenьnik: "pekarьnja" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakeries, bakehouses, baking rooms	piekarni	pekarьnji
noun - jimenьnik: "pekarьnja" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakeries, bakehouses, baking rooms	piekarniach	pekarьnjah
noun - jimenьnik: "pekarьnja" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakeries, bakehouses, baking rooms	piekarniom	pekarьnjam
noun - jimenьnik: "pekarьnja" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakeries, bakehouses, baking rooms	piekarniami	pekarьnjami
noun - jimenьnik: "pekarьnja" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	bakeries, bakehouses, baking rooms	piekarnie	pekarьnje
noun - jimenьnik: "storžьnik" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	strażnik	storžьnik
noun - jimenьnik: "storžьnik" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	strażnika	storžьnika
noun - jimenьnik: "storžьnik" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	strażnika	storžьnika
noun - jimenьnik: "storžьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	strażniku	storžьniče
noun - jimenьnik: "storžьnik" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	strażnikowi	storžьniku
noun - jimenьnik: "storžьnik" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	strażnikiem	storžьnikom
noun - jimenьnik: "storžьnik" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	strażniku	storžniče
noun - jimenьnik: "storžьnik" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	strażnicy	storžьnici
noun - jimenьnik: "storžьnik" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	strażników	storžьniky
noun - jimenьnik: "storžьnik" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	strażników	storžьnik
noun - jimenьnik: "storžьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	strażnikach	storžьnicěh
noun - jimenьnik: "storžьnik" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	strażnikom	storžьnikom
noun - jimenьnik: "storžьnik" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	strażnikami	storžьniky
noun - jimenьnik: "storžьnik" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	strażnicy	storžьnici
noun - jimenьnik: "storžьnik" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	wartownik	storžьnik
noun - jimenьnik: "storžьnik" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	wartownika	storžьnika
noun - jimenьnik: "storžьnik" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	wartownika	storžьnika
noun - jimenьnik: "storžьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	wartowniku	storžьniče
noun - jimenьnik: "storžьnik" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	wartownikowi	storžьniku
noun - jimenьnik: "storžьnik" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	wartownikiem	storžьnikom
noun - jimenьnik: "storžьnik" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	wartowniku	storžniče
noun - jimenьnik: "storžьnik" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	wartownicy	storžьnici
noun - jimenьnik: "storžьnik" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	wartowników	storžьniky
noun - jimenьnik: "storžьnik" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	wartowników	storžьnik
noun - jimenьnik: "storžьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	wartownikach	storžьnicěh
noun - jimenьnik: "storžьnik" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	wartownikom	storžьnikom
noun - jimenьnik: "storžьnik" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	wartownikami	storžьniky
noun - jimenьnik: "storžьnik" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	wartownicy	storžьnici
noun - jimenьnik: "storžьnik" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	gwardzista	storžьnik
noun - jimenьnik: "storžьnik" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	gwardzistę	storžьnika
noun - jimenьnik: "storžьnik" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	gwardzisty	storžьnika
noun - jimenьnik: "storžьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	gwardziście	storžьniče
noun - jimenьnik: "storžьnik" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	gwardziście	storžьniku
noun - jimenьnik: "storžьnik" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	gwardzistą	storžьnikom
noun - jimenьnik: "storžьnik" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsman	gwardzisto	storžniče
noun - jimenьnik: "storžьnik" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	gwardziści	storžьnici
noun - jimenьnik: "storžьnik" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	gwardzistów	storžьniky
noun - jimenьnik: "storžьnik" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	gwardzistów	storžьnik
noun - jimenьnik: "storžьnik" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	gwardzistach	storžьnicěh
noun - jimenьnik: "storžьnik" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	gwardzistom	storžьnikom
noun - jimenьnik: "storžьnik" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	gwardzistami	storžьniky
noun - jimenьnik: "storžьnik" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	guardsmen	gwardziści	storžьnici
noun - jimenьnik: "lice" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	lice	lice
noun - jimenьnik: "lice" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	lice	lice
noun - jimenьnik: "lice" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	lica	lica
noun - jimenьnik: "lice" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	licu	lici
noun - jimenьnik: "lice" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	licu	licu
noun - jimenьnik: "lice" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	licem	licemь
noun - jimenьnik: "lice" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	lice	lice
noun - jimenьnik: "lice" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	lica	lica
noun - jimenьnik: "lice" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	lica	lica
noun - jimenьnik: "lice" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	lic	lic
noun - jimenьnik: "lice" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	licach	licih
noun - jimenьnik: "lice" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	licom	licem
noun - jimenьnik: "lice" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	licami	lici
noun - jimenьnik: "lice" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	lica	lica
noun - jimenьnik: "lice" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	twarz	lice
noun - jimenьnik: "lice" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	twarz	lice
noun - jimenьnik: "lice" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	twarzy	lica
noun - jimenьnik: "lice" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	twarzy	lici
noun - jimenьnik: "lice" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	twarzy	licu
noun - jimenьnik: "lice" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	twarzą	licemь
noun - jimenьnik: "lice" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	face	twarzo	lice
noun - jimenьnik: "lice" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	twarze	lica
noun - jimenьnik: "lice" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	twarze	lica
noun - jimenьnik: "lice" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	twarzy	lic
noun - jimenьnik: "lice" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	twarzach	licih
noun - jimenьnik: "lice" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	twarzom	licem
noun - jimenьnik: "lice" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	twarzami	lici
noun - jimenьnik: "lice" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	faces	twarze	lica
noun - jimenьnik: "bog" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	god	bóg	bog
noun - jimenьnik: "bog" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	god	boga	boga
noun - jimenьnik: "bog" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	god	boga	boga
noun - jimenьnik: "bog" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	god	bogu	bodzě
noun - jimenьnik: "bog" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	god	bogu	bogu
noun - jimenьnik: "bog" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	god	bogiem	bogom
noun - jimenьnik: "bog" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	god	boże	bože
noun - jimenьnik: "bog" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gods	bogowie	bogi
noun - jimenьnik: "bog" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gods	bogów	bogy
noun - jimenьnik: "bog" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gods	bogów	bog
noun - jimenьnik: "bog" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gods	bogach	bodzěh
noun - jimenьnik: "bog" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gods	bogom	bogom
noun - jimenьnik: "bog" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gods	bogami	bogy
noun - jimenьnik: "bog" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	gods	bogowie	bogi
noun - jimenьnik: "drug" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	druch	drug
noun - jimenьnik: "drug" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	drucha	druga
noun - jimenьnik: "drug" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	drucha	druga
noun - jimenьnik: "drug" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	druchu	drudzě
noun - jimenьnik: "drug" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	druchu	drugu
noun - jimenьnik: "drug" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	druchem	drugom
noun - jimenьnik: "drug" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	druchu	druže
noun - jimenьnik: "drug" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	druchowie	drugi
noun - jimenьnik: "drug" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	druchów	drugy
noun - jimenьnik: "drug" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	druchów	drug
noun - jimenьnik: "drug" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	druchach	drudzěh
noun - jimenьnik: "drug" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	druchom	drugom
noun - jimenьnik: "drug" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	druchami	drugy
noun - jimenьnik: "drug" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	druchowie	drugi
noun - jimenьnik: "drug" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	kolega	drug
noun - jimenьnik: "drug" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	kolegę	druga
noun - jimenьnik: "drug" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	kolegi	druga
noun - jimenьnik: "drug" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	koledze	drudzě
noun - jimenьnik: "drug" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	koledze	drugu
noun - jimenьnik: "drug" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	kolegą	drugom
noun - jimenьnik: "drug" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleague, comrade	kolego	druže
noun - jimenьnik: "drug" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	koledzy	drugi
noun - jimenьnik: "drug" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	kolegów	drugy
noun - jimenьnik: "drug" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	kolegów	drug
noun - jimenьnik: "drug" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	kolegach	drudzěh
noun - jimenьnik: "drug" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	kolegom	drugom
noun - jimenьnik: "drug" | instrumental - orǫdьnik (su kym? su čim? o kom? o čim?) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	kolegami	drugy
noun - jimenьnik: "drug" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animacy) - rodjajь mǫžьsky (životьny)	colleagues, comrades	koledzy	drugi
noun - jimenьnik: "rěka" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	river	rzeka	rěka
noun - jimenьnik: "rěka" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	river	rzekę	rěkǫ
noun - jimenьnik: "rěka" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	river	rzeki	rěky
noun - jimenьnik: "rěka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	river	rzece	rěcě
noun - jimenьnik: "rěka" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	river	rzece	rěcě
noun - jimenьnik: "rěka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	river	rzeką	rěkojǫ
noun - jimenьnik: "rěka" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	river	rzeko	rěko
noun - jimenьnik: "rěka" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	rivers	rzeki	rěky
noun - jimenьnik: "rěka" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	rivers	rzeki	rěky
noun - jimenьnik: "rěka" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	rivers	rzek	rěk
noun - jimenьnik: "rěka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	rivers	rzekach	rěkah
noun - jimenьnik: "rěka" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	rivers	rzekom	rěkam
noun - jimenьnik: "rěka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	rivers	rzekami	rěky
noun - jimenьnik: "rěka" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	rivers	rzeki	rěky
noun - jimenьnik: "vojisko" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	army, military	wojsko	vojisko
noun - jimenьnik: "vojisko" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	army, military	wojsko	vojisko
noun - jimenьnik: "vojisko" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	army, military	wojska	vojiska
noun - jimenьnik: "vojisko" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	army, military	wojsku	vojiscě
noun - jimenьnik: "vojisko" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	army, military	wojsku	vojisku
noun - jimenьnik: "vojisko" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	army, military	wojskiem	vojiskomь
noun - jimenьnik: "vojisko" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	army, military	wojsko	vojisko
noun - jimenьnik: "vojisko" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	armies, militaries	wojska	vojiska
noun - jimenьnik: "vojisko" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	armies, militaries	wojska	vojiska
noun - jimenьnik: "vojisko" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	armies, militaries	wojsk	vojisk
noun - jimenьnik: "vojisko" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	armies, militaries	wojskach	vojiscěh
noun - jimenьnik: "vojisko" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	armies, militaries	wojskom	vojiskom
noun - jimenьnik: "vojisko" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	armies, militaries	wojskami	vojisky
noun - jimenьnik: "vojisko" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	armies, militaries	wojska	vojiska
noun - jimenьnik: "dinь" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	day	dzień	dinь
noun - jimenьnik: "dinь" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	day	dzień	dinь
noun - jimenьnik: "dinь" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	day	dnia	dine
noun - jimenьnik: "dinь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	day	dniu	dini
noun - jimenьnik: "dinь" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	day	dniowi/dniu	dini
noun - jimenьnik: "dinь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	day	dniem	dinimь
noun - jimenьnik: "dinь" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	day	dniu	dinь
noun - jimenьnik: "dinь" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	days	dni/dnie	dine
noun - jimenьnik: "dinь" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	days	dni/dnie	dini
noun - jimenьnik: "dinь" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	days	dni	dini
noun - jimenьnik: "dinь" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	days	dniach	dinih
noun - jimenьnik: "dinь" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	days	dniom	dinim
noun - jimenьnik: "dinь" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	days	dniami	dinьmi
noun - jimenьnik: "dinь" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	days	dni/dnie	dine
noun - jimenьnik: "poludine" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	midday	południe	poludine
noun - jimenьnik: "poludine" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	midday	południe	poludine
noun - jimenьnik: "poludine" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	midday	południa	poludina
noun - jimenьnik: "poludine" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	midday	południu	poludini
noun - jimenьnik: "poludine" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	midday	południu	poludini
noun - jimenьnik: "poludine" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	midday	południem	poludinimь
noun - jimenьnik: "poludine" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	midday	południe	poludine
noun - jimenьnik: "poludine" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	middays	południa	poludina
noun - jimenьnik: "poludine" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	middays	południa	poludina
noun - jimenьnik: "poludine" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	middays	południ	poludini
noun - jimenьnik: "poludine" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	middays	południach	poludinih
noun - jimenьnik: "poludine" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	middays	południom	poludinim
noun - jimenьnik: "poludine" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	middays	południami	poludinьmi
noun - jimenьnik: "poludine" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	middays	południa	poludina
noun - jimenьnik: "popoludine" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoon	popołudnie	popoludine
noun - jimenьnik: "popoludine" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoon	popołudnie	popoludine
noun - jimenьnik: "popoludine" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoon	popołudnia	popoludina
noun - jimenьnik: "popoludine" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoon	popołudniu	popoludini
noun - jimenьnik: "popoludine" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoon	popołudniu	popoludini
noun - jimenьnik: "popoludine" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoon	popołudniem	popoludinimь
noun - jimenьnik: "popoludine" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoon	popołudnie	popoludine
noun - jimenьnik: "popoludine" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoons	popołudnia	popoludina
noun - jimenьnik: "popoludine" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoons	popołudnia	popoludina
noun - jimenьnik: "popoludine" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoons	popołudni	popoludini
noun - jimenьnik: "popoludine" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoons	popołudniach	popoludinih
noun - jimenьnik: "popoludine" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoons	popołudniom	popoludinim
noun - jimenьnik: "popoludine" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoons	popołudniami	popoludinьmi
noun - jimenьnik: "popoludine" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	afternoons	popołudnia	popoludina
noun - jimenьnik: "duša | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	dusza	duša
noun - jimenьnik: "duša | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszę	dušǫ
noun - jimenьnik: "duša | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszy	duši
noun - jimenьnik: "duša | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszy	duši
noun - jimenьnik: "duša | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszy	duši
noun - jimenьnik: "duša | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszą	dušejǫ
noun - jimenьnik: "duša | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	soul	duszo	duše
noun - jimenьnik: "duša | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusze	duše
noun - jimenьnik: "duša | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusze	duše
noun - jimenьnik: "duša | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusz	duš
noun - jimenьnik: "duša | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	duszach	dušah
noun - jimenьnik: "duša | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	duszom	dušam
noun - jimenьnik: "duša | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	duszami	dušami
noun - jimenьnik: "duša | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (inanimate) - rodjajь ženьsky (neživotьny)	souls	dusze	duše
noun - jimenьnik: "město" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	place	miejsce	město
noun - jimenьnik: "město" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	place	miejsce	město
noun - jimenьnik: "město" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	place	miejsca	města
noun - jimenьnik: "město" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	place	miejscu	městě
noun - jimenьnik: "město" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	place	miejscu	městu
noun - jimenьnik: "město" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	place	miejscem	městomь
noun - jimenьnik: "město" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	place	miejsce	město
noun - jimenьnik: "město" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	places	miejsca	města
noun - jimenьnik: "město" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	places	miejsca	města
noun - jimenьnik: "město" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	places	miejsc	měst
noun - jimenьnik: "město" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	places	miejscach	městěh
noun - jimenьnik: "město" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	places	miejscom	městom
noun - jimenьnik: "město" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	places	miejscami	městy
noun - jimenьnik: "město" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	places	miejsca	města
noun - jimenьnik: "selo" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	village, hamlet	wieś	selo
noun - jimenьnik: "selo" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	village, hamlet	wieś	selo
noun - jimenьnik: "selo" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	village, hamlet	wsi	sela
noun - jimenьnik: "selo" | locative - selьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	village, hamlet	wsi	selě
noun - jimenьnik: "selo" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	village, hamlet	wsi	selu
noun - jimenьnik: "selo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	village, hamlet	wsią	selomь
noun - jimenьnik: "selo" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	village, hamlet	wieś	selo
noun - jimenьnik: "selo" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	villages, hamlets	wsie/wsi	sela
noun - jimenьnik: "selo" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	villages, hamlets	wsie/wsi	sela
noun - jimenьnik: "selo" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	villages, hamlets	wsi	sel
noun - jimenьnik: "selo" | locative - selьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	villages, hamlets	wsiach	selěh
noun - jimenьnik: "selo" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	villages, hamlets	wsiom	selom
noun - jimenьnik: "selo" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	villages, hamlets	wsiami	sely
noun - jimenьnik: "selo" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	villages, hamlets	wsie/wsi	sela
noun - jimenьnik: "duh" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghost, spirit	duch	duh
noun - jimenьnik: "duh" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghost, spirit	ducha	duha
noun - jimenьnik: "duh" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghost, spirit	ducha	duha
noun - jimenьnik: "duh" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghost, spirit	duchu	duśě
noun - jimenьnik: "duh" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghost, spirit	duchowi	duhu
noun - jimenьnik: "duh" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghost, spirit	duchem	duhomь
noun - jimenьnik: "duh" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghost, spirit	duchu	duše
noun - jimenьnik: "duh" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghosts, spirits	duchy	duśi
noun - jimenьnik: "duh" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghosts, spirits	duchy	duhy
noun - jimenьnik: "duh" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghosts, spirits	duchów	duh
noun - jimenьnik: "duh" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghosts, spirits	duchach	duśěh
noun - jimenьnik: "duh" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghosts, spirits	duchom	duhom
noun - jimenьnik: "duh" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghosts, spirits	duchami	duhy
noun - jimenьnik: "duh" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	ghosts, spirits	duchy	duśi
noun - jimenьnik: "muha" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	fly as insect	mucha	muha
noun - jimenьnik: "muha" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	fly as insect	muchę	muhǫ
noun - jimenьnik: "muha" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	fly as insect	muchy	muhy
noun - jimenьnik: "muha" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	fly as insect	musze	muśě
noun - jimenьnik: "muha" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	fly as insect	musze	muśě
noun - jimenьnik: "muha" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	fly as insect	muchą	muhojǫ
noun - jimenьnik: "muha" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	fly as insect	mucho	muho
noun - jimenьnik: "muha" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	flies as insects	muchy	muhy
noun - jimenьnik: "muha" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	flies as insects	muchy	muhy
noun - jimenьnik: "muha" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	flies as insects	much	muh
noun - jimenьnik: "muha" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	flies as insects	muchach	muhah
noun - jimenьnik: "muha" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	flies as insects	muchom	muham
noun - jimenьnik: "muha" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	flies as insects	muchami	muhami
noun - jimenьnik: "muha" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	flies as insects	muchy	muhy
noun - jimenьnik: "kamy" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stone	kamień	kamy
noun - jimenьnik: "kamy" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stone	kamień	kamenь
noun - jimenьnik: "kamy" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stone	kamienia	kamene
noun - jimenьnik: "kamy" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stone	kamieniu	kamene
noun - jimenьnik: "kamy" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stone	kamieniu	kameni
noun - jimenьnik: "kamy" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stone	kamieniem	kamenimь
noun - jimenьnik: "kamy" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stone	kamień	kamy
noun - jimenьnik: "kamy" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stones	kamienie	kamene
noun - jimenьnik: "kamy" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stones	kamienie	kameni
noun - jimenьnik: "kamy" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stones	kamieni	kamen
noun - jimenьnik: "kamy" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stones	kamieniach	kamenih
noun - jimenьnik: "kamy" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stones	kamieniom	kamenim
noun - jimenьnik: "kamy" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stones	kamieniami	kamenьmi
noun - jimenьnik: "kamy" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	stones	kamienie	kamene
noun - jimenьnik: "greby" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	comb	grzebień	greby
noun - jimenьnik: "greby" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	comb	grzebień	grebenь
noun - jimenьnik: "greby" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	comb	grzebienia	grebene
noun - jimenьnik: "greby" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	comb	grzebieniu	grebene
noun - jimenьnik: "greby" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	comb	grzebieniu	grebeni
noun - jimenьnik: "greby" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	comb	grzebieniem	grebenimь
noun - jimenьnik: "greby" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	comb	grzebień	greby
noun - jimenьnik: "greby" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	combs	grzebienie	grebene
noun - jimenьnik: "greby" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	combs	grzebienie	grebeni
noun - jimenьnik: "greby" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	combs	grzebieni	greben
noun - jimenьnik: "greby" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	combs	grzebieniach	grebenih
noun - jimenьnik: "greby" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	combs	grzebieniom	grebenim
noun - jimenьnik: "greby" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	combs	grzebieniami	grebenьmi
noun - jimenьnik: "greby" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter (inanimate) - rodjajь nijaky (neživotьny)	combs	grzebienie	grebene
noun - jimenьnik: "slověnin" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianman/slovian man/slavic man/slavicman	słowianin	slověnin
noun - jimenьnik: "slověnin" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianman/slovian man/slavic man/slavicman	słowianina	slověnina
noun - jimenьnik: "slověnin" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianman/slovian man/slavic man/slavicman	słowianina	slověnina
noun - jimenьnik: "slověnin" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianman/slovian man/slavic man/slavicman	słowianinie	slověnině
noun - jimenьnik: "slověnin" | dative - měrьnik (komu? czemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianman/slovian man/slavic man/slavicman	słowianinowi	slověninu
noun - jimenьnik: "slověnin" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianman/slovian man/slavic man/slavicman	słowianinem	slověninomь
noun - jimenьnik: "slověnin" | vocative - zovateljь (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianman/slovian man/slavic man/slavicman	słowianinie	slověnine
noun - jimenьnik: "slověnin" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianmen/slovian men/slavic men/slavicmen	słowianie	slověne
noun - jimenьnik: "slověnin" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianmen/slovian men/slavic men/slavicmen	słowian	slověny
noun - jimenьnik: "slověnin" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianmen/slovian men/slavic men/slavicmen	słowian	slověn
noun - jimenьnik: "slověnin" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianmen/slovian men/slavic men/slavicmen	słowianach	slověnih
noun - jimenьnik: "slověnin" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianmen/slovian men/slavic men/slavicmen	słowianom	slověnom
noun - jimenьnik: "slověnin" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianmen/slovian men/slavic men/slavicmen	słowianami	slověny
noun - jimenьnik: "slověnin" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	slovianmen/slovian men/slavic men/slavicmen	słowianie	slověne
noun - jimenьnik: "slověnoka" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwoman/slovian woman/slavic woman/slavicwoman	słowianka	slověnoka
noun - jimenьnik: "slověnoka" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwoman/slovian woman/slavic woman/slavicwoman	słowiankę	slověnokǫ
noun - jimenьnik: "slověnoka" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwoman/slovian woman/slavic woman/slavicwoman	słowianki	slověnoky
noun - jimenьnik: "slověnoka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwoman/slovian woman/slavic woman/slavicwoman	słowiance	slověnocě
noun - jimenьnik: "slověnoka" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwoman/slovian woman/slavic woman/slavicwoman	słowiance	slověnocě
noun - jimenьnik: "slověnoka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwoman/slovian woman/slavic woman/slavicwoman	słowianką	slověnokojǫ
noun - jimenьnik: "slověnoka" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwoman/slovian woman/slavic woman/slavicwoman	słowianko	slověnoko
noun - jimenьnik: "slověnoka" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwomen/slovian women/slavic women/slavicwomen	słowianki	slověnoky
noun - jimenьnik: "slověnoka" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwomen/slovian women/slavic women/slavicwomen	słowianki	slověnoky
noun - jimenьnik: "slověnoka" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwomen/slovian women/slavic women/slavicwomen	słowianek	slověnok
noun - jimenьnik: "slověnoka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwomen/slovian women/slavic women/slavicwomen	słowiankach	slověnokah
noun - jimenьnik: "slověnoka" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwomen/slovian women/slavic women/slavicwomen	słowiankom	slověnokam
noun - jimenьnik: "slověnoka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwomen/slovian women/slavic women/slavicwomen	słowiankami	slověnokami
noun - jimenьnik: "slověnoka" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	slovianwomen/slovian women/slavic women/slavicwomen	słowianki	slověnoky
noun - jimenьnik: "zatoka" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bay, cove, gulf (body of water (especially the sea)	zatoka	zatoka
noun - jimenьnik: "zatoka" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bay, cove, gulf (body of water (especially the sea)	zatokę	zatokǫ
noun - jimenьnik: "zatoka" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bay, cove, gulf (body of water (especially the sea)	zatoki	zatoky
noun - jimenьnik: "zatoka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bay, cove, gulf (body of water (especially the sea)	zatoce	zatocě
noun - jimenьnik: "zatoka" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bay, cove, gulf (body of water (especially the sea)	zatoce	zatocě
noun - jimenьnik: "zatoka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bay, cove, gulf (body of water (especially the sea)	zatoką	zatokojǫ
noun - jimenьnik: "zatoka" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bay, cove, gulf (body of water (especially the sea)	zatoko	zatoko
noun - jimenьnik: "zatoka" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bays, coves, gulfs (bodies of water (especially seas)	zatoki	zatoky
noun - jimenьnik: "zatoka" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bays, coves, gulfs (bodies of water (especially seas)	zatoki	zatoky
noun - jimenьnik: "zatoka" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bays, coves, gulfs (bodies of water (especially seas)	zatok	zatok
noun - jimenьnik: "zatoka" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bays, coves, gulfs (bodies of water (especially seas)	zatokach	zatokah
noun - jimenьnik: "zatoka" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bays, coves, gulfs (bodies of water (especially seas)	zatokom	zatokam
noun - jimenьnik: "zatoka" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bays, coves, gulfs (bodies of water (especially seas)	zatokami	zatokami
noun - jimenьnik: "zatoka" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	bays, coves, gulfs (bodies of water (especially seas)	zatoki	zatoky
noun - jimenьnik: "baba" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old woman	baba	baba
noun - jimenьnik: "baba" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old woman	babę	babǫ
noun - jimenьnik: "baba" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old woman	baby	baby
noun - jimenьnik: "baba" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old woman	babie	babě
noun - jimenьnik: "baba" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old woman	babie	babě
noun - jimenьnik: "baba" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old woman	babą	babojǫ
noun - jimenьnik: "baba" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old woman	babo	babo
noun - jimenьnik: "baba" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old women	baby	baby
noun - jimenьnik: "baba" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old women	baby	baby
noun - jimenьnik: "baba" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old women	bab	bab
noun - jimenьnik: "baba" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old women	babach	babah
noun - jimenьnik: "baba" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old women	babom	babam
noun - jimenьnik: "baba" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old women	babami	babami
noun - jimenьnik: "baba" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine (animacy) - rodjajь ženьsky (životьny)	old women	baby	baby
noun - jimenьnik: "pis" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dog	pies	pis
noun - jimenьnik: "pis" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dog	psa	pьsa
noun - jimenьnik: "pis" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dog	psa	pьsa
noun - jimenьnik: "pis" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dog	psu	pьsě
noun - jimenьnik: "pis" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dog	psu	pьsu
noun - jimenьnik: "pis" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dog	psem	pьsomь
noun - jimenьnik: "pis" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dog	psie	pьse
noun - jimenьnik: "pis" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dogs	psy	pьsi
noun - jimenьnik: "pis" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dogs	psy	pьsy
noun - jimenьnik: "pis" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dogs	psów	pis
noun - jimenьnik: "pis" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dogs	psach	pьsěh
noun - jimenьnik: "pis" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dogs	psom	pьsom
noun - jimenьnik: "pis" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dogs	psami	pьsy
noun - jimenьnik: "pis" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	dogs	psy	pьsi
noun - jimenьnik: "šiv" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seam	szew	šiv
noun - jimenьnik: "šiv" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seam	szew	šiv
noun - jimenьnik: "šiv" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seam	szwa	šьva
noun - jimenьnik: "šiv" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seam	szwie	šьvě
noun - jimenьnik: "šiv" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seam	szwu	šьvu
noun - jimenьnik: "šiv" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seam	szwem	šьvomь
noun - jimenьnik: "šiv" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seam	szwie	šьve
noun - jimenьnik: "šiv" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seams	szwy	šьvi
noun - jimenьnik: "šiv" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seams	szwy	šьvy
noun - jimenьnik: "šiv" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seams	szwów	šiv
noun - jimenьnik: "šiv" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seams	szwach	šьvěh
noun - jimenьnik: "šiv" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seams	szwom	šьvom
noun - jimenьnik: "šiv" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seams	szwami	šьvy
noun - jimenьnik: "šiv" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine (inanimate) - rodjajь mǫžьsky (neživotьny)	seams	szwy	šьvi
noun - jimenьnik: "čelověk" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	human	człowiek	čelověk
noun - jimenьnik: "čelověk" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	human	człowieka	čelověka
noun - jimenьnik: "čelověk" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	human	człowieka	čelověka
noun - jimenьnik: "čelověk" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	human	człowieku	čelověcě
noun - jimenьnik: "čelověk" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	human	człowiekowi	čelověku
noun - jimenьnik: "čelověk" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	human	człowiekiem	čelověkomь
noun - jimenьnik: "čelověk" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	human	człowieku/człowiecze	čelověče
noun - jimenьnik: "ljudьje" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	humans, just people who are not necessarily from the same nation	ludzie	ljudьje
noun - jimenьnik: "ljudьje" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	humans, just people who are not necessarily from the same nation	ludzi	ljudi
noun - jimenьnik: "ljudьje" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	humans, just people who are not necessarily from the same nation	ludzi	ljudьji
noun - jimenьnik: "ljudьje" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	humans, just people who are not necessarily from the same nation	ludziach	ljudih
noun - jimenьnik: "ljudьje" | dative - měrьnik (komu? czemu?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	humans, just people who are not necessarily from the same nation	ludziom	ljudim
noun - jimenьnik: "ljudьje" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	humans, just people who are not necessarily from the same nation	ludźmi	ljudьmi
noun - jimenьnik: "ljudьje" | vocative - zovateljь (o!) | plural - munoga ličьba | type masculine (animate) - rodjajь mǫžьsky (životьny)	humans, just people who are not necessarily from the same nation	ludzie	ljudьje
adjective - pridavьnik: "slověnьsky" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiański	slověnьsky
adjective - pridavьnik: "slověnьsky" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiański	slověnьsky
adjective - pridavьnik: "slověnьsky" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskiego	slověnьskogo
adjective - pridavьnik: "slověnьsky" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskim	slověnьskom
adjective - pridavьnik: "slověnьsky" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskiemu	slověnьskomu
adjective - pridavьnik: "slověnьsky" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskim	slověnьskymь
adjective - pridavьnik: "slověnьsky" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiański	slověnьsky
adjective - pridavьnik: "slověnьsky" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańscy	slověnьsci
adjective - pridavьnik: "slověnьsky" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskich	slověnьskyh
adjective - pridavьnik: "slověnьsky" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskich	slověnьskyh
adjective - pridavьnik: "slověnьsky" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskich	slověnьskyh
adjective - pridavьnik: "slověnьsky" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskim	slověnьskymь
adjective - pridavьnik: "slověnьsky" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańskimi	slověnьskymi
adjective - pridavьnik: "slověnьsky" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	slovian, slavic	słowiańscy	slověnьsci
adjective - pridavьnik: "slověnьsky" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańska	slověnьska
adjective - pridavьnik: "slověnьsky" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańską	slověnьskǫ
adjective - pridavьnik: "slověnьsky" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskiej	slověnьskoji
adjective - pridavьnik: "slověnьsky" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskiej	slověnьskoji
adjective - pridavьnik: "slověnьsky" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskiej	slověnьskoji
adjective - pridavьnik: "slověnьsky" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańską	slověnьskojǫ
adjective - pridavьnik: "slověnьsky" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańska	slověnьska
adjective - pridavьnik: "slověnьsky" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "slověnьsky" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "slověnьsky" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskich	slověnьskyh
adjective - pridavьnik: "slověnьsky" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskich	slověnьskyh
adjective - pridavьnik: "slověnьsky" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskim	slověnьskymь
adjective - pridavьnik: "slověnьsky" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskimi	slověnьskymi
adjective - pridavьnik: "slověnьsky" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine - rodjajь ženьsky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "slověnьsky" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "slověnьsky" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "slověnьsky" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskiego	slověnьskogo
adjective - pridavьnik: "slověnьsky" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskim	slověnьskom
adjective - pridavьnik: "slověnьsky" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskiemu	slověnьskomu
adjective - pridavьnik: "slověnьsky" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskim	slověnьskymь
adjective - pridavьnik: "slověnьsky" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskie	slověnьsko
adjective - pridavьnik: "slověnьsky" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "slověnьsky" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "slověnьsky" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskich	slověnьskyh
adjective - pridavьnik: "slověnьsky" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskich	slověnьskyh
adjective - pridavьnik: "slověnьsky" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskim	slověnьskymь
adjective - pridavьnik: "slověnьsky" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskimi	slověnьskymi
adjective - pridavьnik: "slověnьsky" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter - rodjajь nijaky	slovian, slavic	słowiańskie	slověnьske
adjective - pridavьnik: "boži" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	godly	boży	boži
adjective - pridavьnik: "boži" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	godly	boży	boži
adjective - pridavьnik: "boži" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	godly	bożego	božego
adjective - pridavьnik: "boži" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	godly	bożym	božemь
adjective - pridavьnik: "boži" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	godly	bożemu	božemu
adjective - pridavьnik: "boži" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	godly	bożym	božimь
adjective - pridavьnik: "boži" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	godly	boży	boži
adjective - pridavьnik: "boži" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	godly	boży	boži
adjective - pridavьnik: "boži" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	godly	bożych	božih
adjective - pridavьnik: "boži" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	godly	bożych	božih
adjective - pridavьnik: "boži" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	godly	bożych	božih
adjective - pridavьnik: "boži" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	godly	bożym	božimь
adjective - pridavьnik: "boži" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	godly	bożymi	božimi
adjective - pridavьnik: "boži" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	godly	boży	boži
adjective - pridavьnik: "boži" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	godly	boża	boža
adjective - pridavьnik: "boži" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	godly	bożą	božǫ
adjective - pridavьnik: "boži" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	godly	bożej	božeji
adjective - pridavьnik: "boži" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	godly	bożej	božeji
adjective - pridavьnik: "boži" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	godly	bożej	božeji
adjective - pridavьnik: "boži" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	godly	bożą	božejǫ
adjective - pridavьnik: "boži" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	godly	boża	boža
adjective - pridavьnik: "boži" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	godly	boże	bože
adjective - pridavьnik: "boži" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	godly	boże	bože
adjective - pridavьnik: "boži" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	godly	bożych	božih
adjective - pridavьnik: "boži" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	godly	bożych	božih
adjective - pridavьnik: "boži" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	godly	bożym	božimь
adjective - pridavьnik: "boži" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	godly	bożymi	božimi
adjective - pridavьnik: "boži" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine - rodjajь ženьsky	godly	boże	bože
adjective - pridavьnik: "boži" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	godly	boże	bože
adjective - pridavьnik: "boži" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	godly	boże	bože
adjective - pridavьnik: "boži" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	godly	bożego	božego
adjective - pridavьnik: "boži" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	godly	bożym	božemь
adjective - pridavьnik: "boži" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	godly	bożemu	božemu
adjective - pridavьnik: "boži" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	godly	bożym	božimь
adjective - pridavьnik: "boži" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	godly	boże	bože
adjective - pridavьnik: "boži" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter - rodjajь nijaky	godly	boże	bože
adjective - pridavьnik: "boži" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter - rodjajь nijaky	godly	boże	bože
adjective - pridavьnik: "boži" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter - rodjajь nijaky	godly	bożych	božih
adjective - pridavьnik: "boži" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter - rodjajь nijaky	godly	bożych	božih
adjective - pridavьnik: "boži" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter - rodjajь nijaky	godly	bożym	božimь
adjective - pridavьnik: "boži" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter - rodjajь nijaky	godly	bożymi	božimi
adjective - pridavьnik: "boži" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter - rodjajь nijaky	godly	boże	bože
adjective - pridavьnik: "orvьny" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równy	orvьny
adjective - pridavьnik: "orvьny" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równy	orvьny
adjective - pridavьnik: "orvьny" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równego	orvьnogo
adjective - pridavьnik: "orvьny" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równym	orvьnom
adjective - pridavьnik: "orvьny" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równemu	orvьnomu
adjective - pridavьnik: "orvьny" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równym	orvьnymь
adjective - pridavьnik: "orvьny" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równy	orvьny
adjective - pridavьnik: "orvьny" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równi	orvьni
adjective - pridavьnik: "orvьny" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równych	orvьnyh
adjective - pridavьnik: "orvьny" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równych	orvьnyh
adjective - pridavьnik: "orvьny" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równych	orvьnyh
adjective - pridavьnik: "orvьny" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równym	orvьnymь
adjective - pridavьnik: "orvьny" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równymi	orvьnymi
adjective - pridavьnik: "orvьny" | vocative - zovanьnik (o!) | plural - munoga ličьba | type masculine - rodjajь mǫžьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równi	orvьny
adjective - pridavьnik: "orvьny" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równa	orvьna
adjective - pridavьnik: "orvьny" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równą	orvьnǫ
adjective - pridavьnik: "orvьny" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równej	orvьneji
adjective - pridavьnik: "orvьny" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równej	orvьneji
adjective - pridavьnik: "orvьny" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równej	orvьneji
adjective - pridavьnik: "orvьny" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równą	orvьnejǫ
adjective - pridavьnik: "orvьny" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równa	orvьna
adjective - pridavьnik: "orvьny" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równych	orvьnyh
adjective - pridavьnik: "orvьny" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równych	orvьnyh
adjective - pridavьnik: "orvьny" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równym	orvьnymь
adjective - pridavьnik: "orvьny" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równymi	orvьnymi
adjective - pridavьnik: "orvьny" | vocative - zovanьnik (o!) | plural - munoga ličьba | type feminine - rodjajь ženьsky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | nominative - jimenovьnik (koto? čьto?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | accusative - vinьnik (kogo? čьto?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | genitive - rodilьnik (kogo? čego?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równego	orvьnogo
adjective - pridavьnik: "orvьny" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równym	orvьnom
adjective - pridavьnik: "orvьny" | dative - měrьnik (komu? čemu?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równemu	orvьnomu
adjective - pridavьnik: "orvьny" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równym	orvьnymь
adjective - pridavьnik: "orvьny" | vocative - zovanьnik (o!) | singular - poedinьna ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | nominative - jimenovьnik (koto? čьto?) | plural - munoga ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | accusative - vinьnik (kogo? čьto?) | plural - munoga ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne
adjective - pridavьnik: "orvьny" | genitive - rodilьnik (kogo? čego?) | plural - munoga ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równych	orvьnyh
adjective - pridavьnik: "orvьny" | locative - městьnik (ob kom? ob čem? kude? vu? na? pri?) | plural - munoga ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równych	orvьnyh
adjective - pridavьnik: "orvьny" | dative - měrьnik (komu? čemu?) | plural - munoga ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równym	orvьnymь
adjective - pridavьnik: "orvьny" | instrumental - orǫdьnik (su kymь? su čimь? su jakymь?) | plural - munoga ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równymi	orvьnymi
adjective - pridavьnik: "orvьny" | vocative - zovanьnik (o!) | plural - munoga ličьba | type neuter - rodjajь nijaky	equal (not better or worse than someone else), equal (having the same social situation as someone else)	równe	orvьne

--------------------------------------------------
TOKENIZACJA
--------------------------------------------------

Podziel tekst na tokeny:

- słowa
- liczby
- interpunkcję

--------------------------------------------------
MAPOWANIE PRZYIMKÓW
--------------------------------------------------

w → vu  
z → iz  
ze → iz  
do → do  
od → od  
na → na  
po → po  
przy → pri  

--------------------------------------------------
ROZPOZNAWANIE PRZYPADKU Z POLSKIEJ FORMY
--------------------------------------------------

Wykrywaj przypadek z końcówki polskiego słowa.

LOCATIVE:

-ogrodzie  
-domu  
-lesie  
-mieście  

→ LOC

GENITIVE:

-ogrodu  
-domu  
-lasu  
-miasta  

→ GEN

INSTRUMENTAL:

-ogrodem  
-domem  
-lasem  

→ INS

DATIVE:

-ogrodowi  
-domowi  

→ DAT

ACCUSATIVE:

jeśli identyczne z NOM dla rodzaju nieżywotnego

→ ACC

Jeśli brak przyimka i brak końcówki:

→ NOM

--------------------------------------------------
ALGORYTM
--------------------------------------------------

Dla każdego słowa:

1. znajdź jego podstawę w osnova.json
2. pobierz rdzen
3. pobierz vuzor
4. określ przypadek
5. określ liczbę
6. znajdź końcówkę w vuzor.json

vuzor → liczba → przypadek

7. zbuduj formę

rdzen + koncowka

--------------------------------------------------
PRZYMIOTNIKI
--------------------------------------------------

Przymiotnik musi mieć:

- ten sam przypadek
- tę samą liczbę
- ten sam rodzaj

co rzeczownik.

Przymiotnik zawsze stoi przed rzeczownikiem.

--------------------------------------------------
ZASADY BEZWZGLĘDNE
--------------------------------------------------

1. Nie wolno zgadywać końcówek.

2. Nie wolno tworzyć nowych form.

3. Jeśli słowo nie istnieje w osnova.json zwróć:

(ne najdeno slova)

4. Zachowuj:

- interpunkcję
- wielkie litery
- odstępy
- kolejność zdania

5. Nie dodawaj komentarzy.

6. Nie pokazuj analizy.

--------------------------------------------------
FORMAT
--------------------------------------------------

Zwróć tylko wynikowy tekst.

--------------------------------------------------
PRZYKŁAD

Wejście:

W ogrodzie.

Wynik:

Vu obgordě.
"""

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"LISTA MAPOWANIA:\n{mapping_rules}\n\nTEKST ŹRÓDŁOWY:\n{user_input}"}
                ],
                model="openai/gpt-oss-120b",
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()

            # Wyświetlanie wyniku
            st.markdown("### Vynik perklada:")
            st.success(response_text)

        except Exception as e:
            st.error(f"Błąd modelu: {e}")

        if matches:
            with st.expander("Użyte mapowanie z bazy"):
                for m in matches:
                    st.write(f"'{m['polish']}' → `{m['slovian']}`")


















