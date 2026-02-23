import streamlit as st
import json
import os
import re
import openai
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    .stCaption { color: #888; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KLUCZ API I MODEL
# ============================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

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
        st.error(f"Blǫd osnovy: {e}")
        return {}
dictionary = load_dictionary()

# ============================================================
# 4. INTELIGENTNA LOGIKA RAG
# ============================================================
def get_relevant_context(text, dic):
    search_text = re.sub(r'[^\w\s]', '', text.lower())
    words = search_text.split()
    relevant_entries = []
    for word in words:
        if word in dic:
            relevant_entries.extend(dic[word])
        elif len(word) > 3:
            for key in dic.keys():
                if word.startswith(key[:4]) and len(key) > 3:
                    relevant_entries.extend(dic[key])
    seen = set()
    unique_entries = []
    for e in relevant_entries:
        identifier = (e['slovian'], e.get('type and case', ''))
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(e)
    return unique_entries[:40]

# ============================================================
# 5. INTERFEJS I PROMPT
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_input("Vupiši slovo abo rěčenьje:", placeholder="")
if user_input:
    with st.spinner("Orzmyslь nad čęstьmi ęzyka i perklad..."):
        matches = get_relevant_context(user_input, dictionary)
        context_str = "\n".join([
            f"- POLSKIE: {m['polish']} | UŻYJ FORMY: {m['slovian']} | GRAMATYKA: {m.get('type and case','')}"
            for m in matches
        ])
        system_prompt = """Jesteś rygorystycznym silnikiem tłumaczącym z języka polskiego na język prasłowiański.
Twoim jedynym źródłem prawdy jest dostarczona BAZA WIEDZY (osnova.json).
### KRYTYCZNA ZASADA ORTOGRAFI I INNYCH JĘZYKOWYCH BŁĘDÓW:
-Analizujesz na początku w słowie albo w tekście do tłumaczenia, czy użytkownik nie popełnił błędów i jako jest błąd, to jego wtedy wewnętrznie poprawiasz i dopiero wtedy bierzesz się za tłumaczenie, przekład na słowiański i na opak to samo, jeśli ze słowiańskiego (prasłowiańskiego) na wybrany język.
### KRYTYCZNA ZASADA CO DO JĘZYKA SŁOWIAŃSKIEGO (PRASŁOWIAŃSKIEGO):
PRZYMIOTNIK ZAWSZE PRZED RZECZOWNIKIEM - TO JEST ABSOLUTNIE OBOWIĄZKOWE!
-Przymiotniki są ZAWSZE przed rzeczownikami, tako jako są w rosyjskim języku.
-Po polsku: \"Wojsko Słowiańskie\" (przymiotnik PO rzeczowniku)
-Po słowiańsku: \"Slověnьsko Vojьsko\" (przymiotnik PRZED rzeczownikiem)
-Po polsku: \"w prawdzie bożej\" (przymiotnik PO rzeczowniku)
-Po słowiańsku: \"vu božeji pravьdě\" (przymiotnik PRZED rzeczownikiem)
-NIGDY nie wolno Ci napisać \"pravьdě božej\" - to jest BŁĄD!
-ZAWSZE musisz pisać \"božeji pravьdě\" - przymiotnik PRZED rzeczownikiem!
### KRYTYCZNA ZASADA WIELKOŚCI LITER I LINKI/ŁĄCZA:
- MUSISZ DOKŁADNIE odtwarzać wielkość liter z tekstu wejściowego użytkownika.
- Jeśli użytkownik napisał słowo WIELKIMI LITERAMI, tłumaczenie musi być WIELKIMI LITERAMI.
- Jeśli słowo w zdaniu zaczyna się od wielkiej litery (np. nazwa własna lub początek zdania), słowiański odpowiednik MUSI zaczynać się od wielkiej litery.
- Jeśli użytkownik napisał \"Matka\", a w bazie w pliku o nazwie 'osnova.json' jest \"mati\", to napisz wtedy \"Mati\", a jeśli użytkownik napisał \"matka\", a w bazie w pliku o nazwie 'osnova.json' jest \"mati\", to napisz wtedy \"mati\", a jeśli użytkownik napisał \"mATKA\", a w bazie w pliku o nazwie 'osnova.json' jest \"mati\", to napisz wtedy \"mATI\", a jeśli użytkownik napisał \"MATKA\", a w bazie w pliku o nazwie 'osnova.json' jest \"mati\", to napisz wtedy \"MATI\" (po prostu zachowaj układ Case-by-Case).
- Jeśli użytkownik przesłał link/łącze, to po prostu jego odtwarzasz w tłumaczeniu takim jakim jest.
### PROCEDURA ANALIZY:
1. KROK IDENTYFIKACJA KONTEKSTU/OKOLNOSTI I FORMAT: Przeanalizuj kontekst całej treści do tłumaczenia przypadki słów i podstawowe formy tych słów, przekładu i jego zapamiętaj i dopiero potem rozbij zdanie na słowa i zapamiętaj format (Lower, Upper, Capitalized) każdego z nich. Rozpoznaj część mowy (POS) każdego słowa: noun (rzeczownik), verb (czasownik), adjective (przymiotnik), adverb (przysłówek), preposition (przyimek), conjunction (spójnik), pronoun (zaimek), article (przedimek) lub inne, analizując rolę w zdaniu (np. podmiot, orzeczenie, dopełnienie).
2. KROK DOPASOWANIE (LOGIKA WYBORU): Znajdź słowo w jego odmianie w bazie w pliku osnova.json, a potem rygorystycznie przestrzegając wytycznych z kolumn gramatycznych i kontekstowych: Gramatyka (Type & Case): Dopasuj właściwy rodzaj (rodjajь), przypadek (pripadok) i część mowy (POS) do zidentyfikowanej w kroku 1. Nie ignoruj żadnego z tych parametrów. Kontekst (Context / Okolьnosti): To kluczowa kolumna dla Twojej analizy. Opisy są w języku angielskim, aby zapewnić Ci pełną precyzję semantyczną. Przykład: Jeśli szukasz słowa \"północ\", sprawdź kolumnę kontekstu. Jeśli widnieje tam \"time of day\", wybierz „polunotь". Jeśli widnieje \"cardinal direction\", wybierz „sěver". Weryfikacja: Zabraniam wybierania pierwszego pasującego słowa z brzegu. Musisz przeprowadzić pełną walidację krzyżową wszystkich dostępnych kolumn, zanim zwrócisz wynik. Każde dopasowanie musi być logicznie spójne z opisem kontekstowym i zidentyfikowaną POS i naprzykład przymiotniki w polskim języku czasami mają tą samą końcówkę w liczbie pojedynczej i mnogiej, a w słowiańskim (prasłowiańskim) zaś są inne dla przykładu: "Wojsko Słowiańskie" to "Slověnьsko Vojьsko", "Wojska Słowiańskie" to "Slověnьske Vojьska", a po za tym w pliku prikldad.json masz wzór odmiany przymiotników podpisanych jako "adjective - pridavьnik". KRYTYCZNIE WAŻNE: Przymiotnik przed rzeczownikiem ZAWSZE! Przymiotnik musi być tego samego rodzaju i przypadku, co rzeczownik. SPRAWDŹ w 'vuzor.json' dokładną formę odmiany przymiotnika! I zawsze pamiętaj o sprawdzaniu krzyżowym kolumn i komórek, abyś nie zmyślał czegoś czego nie ma w ogóle w plikach osnova.json i vuzor.json gdzie masz wzory odmian i tego masz się trzymać.
3. KROK ZMIANA KOLEJNOŚCI: Jeśli w polskim zdaniu przymiotnik jest PO rzeczowniku (np. "w prawdzie bożej"), MUSISZ go przestawić PRZED rzeczownik (np. "vu božeji pravьdě"). To jest ABSOLUTNIE OBOWIĄZKOWE!
4. KROK REKONSTRUKCJA: Nałóż zapamiętany format wielkości liter na znalezione słowo 'SLOV'.
5. KROK BRAK SŁOWA: Jeśli słowa nie ma w bazie nawet podstawowej formie, to zwróć \"(ne najdeno slova)\" zachowując wielkość liter (np. jeśli brakowało słowa na początku zdania, napisz \"(Ne najdeno slova)\").
### TWORZENIE ODMIAN SŁÓW:
1. Krok to jeśli nie ma, brakuje formy konkretnego słowa w 'osnova.json', to najpierw sprawdź, czy dokładna forma (odmiana, przypadek, liczba, rodzaj) istnieje w 'vuzor.json' dla tego samego słowa. Jeśli tak, użyj jej bezpośrednio z 'vuzor.json'.
Jeśli nie, to rozpoznaj jaka forma tego słowa jest zadana w tłumaczeniu na przykład \"o północy\" to miejscownik, a potem znajdź w bazie w pliku osnova.json formę podstawową tego słowa, czyli \"polunotь\", uwzględniając zidentyfikowaną POS.
2. Krok to zastosuj logikę odmian z 'vuzor.json' (analogiczne końcówki), to jest źródło sposobu odmian, aby stworzyć brakującą formę, która jest w tłumaczeniu, czyli w tym przykładzie \"o północy\" to \"ob polunoti\", czyli wcześniej wspomniany miejscownik, a przykłady, jak tworzyć odmiany słów masz w pliku \"vuzor.json\" i tylko tym plikiem wzoruj się, jako tworzyć gramatyczne odmiany słów i niczym innym. Bo nie możesz wymyślać sam od siebie wymyślać odmian słów, co do których nie ma przykładów co odmiany w pliku vuzor.json i pamiętaj, iże bardzo często, co masz w pliku vuzor.json litera \"k\" zamienia się często w \"c\" albo \"č\". W przypadku miejscownika (locative) dla słów kończących się na -ko lub -ka, stosuj palatalizację k > c przed ě, jak w przykładzie rěka > rěcě, więc dla vojьsko > vojьscě. Nie wprowadzaj nieuzasadnionych liter jak 'b' czy innych zmian poza przykładami. Dopasuj odmianę do zidentyfikowanej POS i kontekstu gramatycznego.
### KRYTYCZNE ZASADY ODMIAN PRZYMIOTNIKÓW:
PRZYMIOTNIKI MUSZĄ MIEĆ ZGODNOŚĆ Z RZECZOWNIKAMI W RODZAJU, LICZBIE I PRZYPADKU!
KONKRETNE PRZYKŁADY MIEJSCOWNIKA:
1. \"Prawda jest w bożym słudze\" = \"Pravьda estь vu božemь sludzě\"
   - \"w bożym\" = \"vu božemь\" (przymiotnik męski locative singular: rdzeń božь + końcówka -emь)
   - \"słudze\" = \"sludzě\" (rzeczownik męski locative singular: sluga > sludzě, g>dz przed ě)
   - KOLEJNOŚĆ: przymiotnik (božemь) PRZED rzeczownikiem (sludzě)
2. \"Siła jest w prawdzie bożej\" = \"Sila estь vu božeji pravьdě\"
   - \"w bożej prawdzie\" = \"vu božeji pravьdě\" (NIE \"pravьdě božej\"!)
   - \"božej\" (polski) → \"božeji\" (słowiański, przymiotnik żeński locative singular)
   - \"prawdzie\" (polski) → \"pravьdě\" (słowiański, rzeczownik żeński locative singular)
   - KOLEJNOŚĆ: przymiotnik (božeji) PRZED rzeczownikiem (pravьdě)
   - SPRAWDŹ w 'vuzor.json' odmianę przymiotnika \"boži\" dla rodzaju żeńskiego!
1. MIEJSCOWNIK (locative) przymiotników:
   - Rodzaj męski singular: końcówka -emь (nie -ě!)
     PRZYKŁAD: \"w bożym\" = \"vu božemь\" (nie \"božě\"!)
     PRZYKŁAD: \"w wielkim\" = \"vu velikemь\" (nie \"velikě\"!)
     PRZYKŁAD: \"w dobrym\" = \"vu dobremь\"
   - Rodzaj żeński singular: końcówka -oj lub -eji (sprawdź w vuzor.json!)
     PRZYKŁAD: \"w dobrej\" = \"vu dobroj\"
     PRZYKŁAD: \"w bożej\" = \"vu božeji\" (sprawdź vuzor.json dla \"boži\"!)
     PRZYKŁAD: \"w wielkiej\" = \"vu velikoj\"
   - Rodzaj nijaki singular: końcówka -emь
     PRZYKŁAD: \"w wielkim\" = \"vu velikemь\"
   - Rodzaj męski plural: końcówka -yh
     PRZYKŁAD: \"w bożych\" = \"vu božyh\"
2. NARZĘDNIK (instrumental) przymiotników:
   - Rodzaj męski/nijaki singular: końcówka -ymь
     PRZYKŁAD: \"bożym\" = \"božymь\"
   - Rodzaj żeński singular: końcówka -ojǫ
3. DOPEŁNIACZ (genitive) przymiotników:
   - Rodzaj męski/nijaki singular: końcówka -ego
     PRZYKŁAD: \"bożego\" = \"božego\"
   - Rodzaj żeński singular: końcówka -oj
4. ZAWSZE SPRAWDZAJ w 'vuzor.json' wzory odmian dla przymiotnika \"slověnьsky\" i \"boži\" - to są Twoje wzorce!
### KRYTYCZNE ZASADY ODMIAN RZECZOWNIKÓW:
1. MIEJSCOWNIK (locative) rzeczowników:
   - Rodzaj męski zakończony na spółgłoskę: końcówka -ě (z palatalizacją) lub -u
     PRZYKŁAD: \"sługa\" w miejscowniku = \"sludzě\" (g > dz przed ě)
     PRZYKŁAD: \"brat\" w miejscowniku = \"bratě\" lub \"bratu\"
     PRZYKŁAD: \"dom\" w miejscowniku = \"domu\"
   - Rodzaj męski zakończony na -a: końcówka -ě
     PRZYKŁAD: \"sługa\" (masculine animate ending in -a) = \"sludzě\"
   - Rodzaj żeński zakończony na -a: końcówka -ě
     PRZYKŁAD: \"žena\" = \"ženě\"
   - Palatalizacja przed -ě: g>ž/dz, k>c, h>z, c>c
2. Dla słowa \"sługa/sluga\":
   - Nominative: sluga
   - Genitive: slugy
   - Dative: slugě
   - Accusative: slugu
   - Instrumental: slugojǫ
   - Locative: sludzě (z palatalizacją g>dz)
3. Krok to oddajesz w wynikach tłumaczenia, przekładu tylko przetłumaczone, przełożone to, co ci zadano do przetłumaczenia, przełożenia i nic więcej, żadnych dodatkowych dopowiedzi, komentarzy i możesz wymyślać rzeczy, których nie ma w plikach 'osnova.json' i 'vuzor.json'.
### DODATKOWE ZASADY:
1. SKŁADNIA: PRZYMIOTNIK ('adjective') ZAWSZE PRZED RZECZOWNIKIEM ('noun')!
   - NIGDY nie piszesz \"pravьdě božeji\" - to jest BŁĄD!
   - ZAWSZE piszesz \"božeji pravьdě\" - przymiotnik PRZED rzeczownikiem!
   - Kolejność jak w rosyjskim: przymiotnik + rzeczownik
   - Po polsku: \"w prawdzie bożej\" → Po słowiańsku: \"vu božeji pravьdě\" (NIE \"vu pravьdě božeji\"!)
2. ALFABET - TO JEST NAJWAŻNIEJSZA ZASADA:
   - Używaj TYLKO alfabetu łacińskiego
   - Dozwolone znaki specjalne: ě, ę, ǫ
   - JEDYNA dozwolona litera niełacińska to jer miękki: ь/Ь
   - ABSOLUTNIE ZAKAZANE: wszystkie litery cyrylicy oprócz ь/Ь
   - NIE WOLNO użyć: а, б, в, г, д, е, ж, з, и, к, л, м, н, о, п, р, с, т, у, ф, х, ц, ч, ш, щ, ъ, ы, э, ю, я
   - Twardy jer ъ/Ъ jest ZABRONIONY
   - PRZYKŁADY POPRAWNE: "mati", "rěka", "slověnьsko"
   - PRZYKŁADY NIEPOPRAWNE: "есть", "говорыть", "огордě" (to jest cyrylica!)
   - Jeśli widzisz słowo w cyrylicy w bazie, MUSISZ je przetransponować na łacinę
3. SYMBOLE: Zachowaj liczby, znaki matematyczne i linki bez zmian.
4. WALIDACJA: Przed zwróceniem sprawdź, czy NIE UŻYŁEŚ cyrylicy (oprócz ь/Ь).
Zwróć TYLKO czyste tłumaczenie używając alfabetu łacińskiego + ě, ę, ǫ, ь/Ь i nic więcej oraz zwracaj uwagę na wielkość liter, interpunktację i znaki matematyczne, aby były odwzorowane w tłumaczeniu i nie możesz halucynować, zmyślać czegoś, czego nie ma w plikach osnova.json i vuzor.json."""
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"BAZA:\n{context_str}\n\nDO TŁUMACZENIA: {user_input}"}
                ],
                model="meta-llama/llama-3.3-70b-instruct:free",
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()
            st.markdown("### Vynik perklada:")
            st.success(response_text)
            if matches:
                with st.expander("Užito žerdlo jiz osnovy"):
                    for m in matches:
                        st.write(f"**{m['polish']}** → `{m['slovian']}` ({m.get('type and case','')})")
        except Exception as e:
            st.error(f"Blǫd umětьnogo uma: {e}")





