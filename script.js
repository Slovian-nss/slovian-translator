let plToSlo = {}, sloToPl = {};
let wordTypes = {};

const languageData = [
    { code: 'slo', slo: 'Slověnьsky', pl: 'Słowiański', en: 'Slovian (Slavic)', de: 'Slawisch', ru: 'Славянский', fr: 'Slave', es: 'Eslavo', cs: 'Slovanský', sk: 'Slovanský', it: 'Slavo' },
    { code: 'en', slo: "Angol'ьsky", pl: 'Angielski', en: 'English', de: 'Englisch', ru: 'Английский', fr: 'Anglais', es: 'Inglés', cs: 'Angličtina', sk: 'Angličtina', it: 'Inglese' },
    { code: 'pl', slo: "Pol'ьsky", pl: 'Polski', en: 'Polish', de: 'Polnisch', ru: 'Польский', fr: 'Polonais', es: 'Polaco', cs: 'Polština', sk: 'Poľština', it: 'Polacco' },
    { code: 'de', slo: 'Nemьčьsky', pl: 'Niemiecki', en: 'German', de: 'Deutsch', ru: 'Немецкий', fr: 'Allemand', es: 'Alemán', cs: 'Němčina', sk: 'Nemčina', it: 'Tedesco' },
    { code: 'cs', slo: 'Češьsky', pl: 'Czeski', en: 'Czech', de: 'Tschechisch', ru: 'Чешский', fr: 'Tchèque', es: 'Checo', cs: 'Čeština', sk: 'Čeština', it: 'Ceco' },
    { code: 'sk', slo: 'Slovačьsky', pl: 'Słowacki', en: 'Slovak', de: 'Slowakisch', ru: 'Словацкий', fr: 'Slovaque', es: 'Eslovaco', cs: 'Slovenština', sk: 'Slovenčina', it: 'Slovacco' },
    { code: 'ru', slo: 'Rusьsky', pl: 'Rosyjski', en: 'Russian', de: 'Russisch', ru: 'Русский', fr: 'Russe', es: 'Ruso', cs: 'Ruština', sk: 'Ruština', it: 'Russo' },
    { code: 'uk', slo: 'Ukrajinьsky', pl: 'Ukraiński', en: 'Ukrainian', de: 'Ukrainisch', ru: 'Украинский', fr: 'Ukrainien', es: 'Ucraniano', cs: 'Ukrajinština', sk: 'Ukrajinčina', it: 'Ucraino' },
    { code: 'be', slo: 'Bělorusьsky', pl: 'Białoruski', en: 'Belarusian', de: 'Weißrussisch', ru: 'Белорусский', fr: 'Biélorusse', es: 'Bielorruso', cs: 'Běloruština', sk: 'Bieloruština', it: 'Bielorusso' },
    { code: 'bg', slo: "Boulgar'ьsky", pl: 'Bułgarski', en: 'Bulgarian', de: 'Bulgarisch', ru: 'Болгарский', fr: 'Bulgare', es: 'Búlgaro', cs: 'Bulharština', sk: 'Bulharčina', it: 'Bulgaro' },
    { code: 'hr', slo: 'Horvatьsky', pl: 'Chorwacki', en: 'Croatian', de: 'Kroatisch', ru: 'Хорватский', fr: 'Croate', es: 'Croata', cs: 'Chorvatština', sk: 'Chorvátština', it: 'Croato' },
    { code: 'sr', slo: 'Sirbьsky', pl: 'Serbski', en: 'Serbian', de: 'Serbisch', ru: 'Сербский', fr: 'Serbe', es: 'Serbio', cs: 'Srbština', sk: 'Srbčina', it: 'Serbo' },
    { code: 'sl', slo: 'Slovenečьsky', pl: 'Słoweński', en: 'Slovenian', de: 'Slowenisch', ru: 'Словенский', fr: 'Slovène', es: 'Esloveno', cs: 'Slovinština', sk: 'Slovinčina', it: 'Sloveno' },
    { code: 'mk', slo: 'Makedonьsky', pl: 'Macedoński', en: 'Macedonian', de: 'Mazedonisch', ru: 'Македонский', fr: 'Macédonien', es: 'Macedonio', cs: 'Makedonština', sk: 'Macedónčina', it: 'Macedone' },
    { code: 'fr', slo: 'Franьsky', pl: 'Francuski', en: 'French', de: 'Französisch', ru: 'Французский', fr: 'Français', es: 'Francés', cs: 'Francouzština', sk: 'Francúzština', it: 'Francese' },
    { code: 'es', slo: 'Španьsky', pl: 'Hiszpański', en: 'Spanish', de: 'Spanisch', ru: 'Испанский', fr: 'Espagnol', es: 'Español', cs: 'Španělština', sk: 'Španielčina', it: 'Spagnolo' },
    { code: 'it', slo: 'Volšьsky', pl: 'Włoski', en: 'Italian', de: 'Italienisch', ru: 'Итальянский', fr: 'Italien', es: 'Italiano', cs: 'Italština', sk: 'Taliančina', it: 'Italiano' },
    { code: 'pt', slo: "Portugal'ьsky", pl: 'Portugalski', en: 'Portuguese', de: 'Portugiesisch', ru: 'Португальский', fr: 'Portugais', es: 'Portugués', cs: 'Portugalština', sk: 'Portugalčina', it: 'Portoghese' },
    { code: 'nl', slo: 'Niskozemьsky', pl: 'Holenderski', en: 'Dutch', de: 'Niederländisch', ru: 'Нидерландский', fr: 'Néerlandais', es: 'Neerlandés', cs: 'Nizozemština', sk: 'Holandčina', it: 'Olandese' },
    { code: 'da', slo: 'Dunьsky', pl: 'Duński', en: 'Danish', de: 'Dänisch', ru: 'Датский', fr: 'Danois', es: 'Danés', cs: 'Dánština', sk: 'Dánčina', it: 'Danese' },
    { code: 'sv', slo: 'Švedьsky', pl: 'Szwedzki', en: 'Swedish', de: 'Schwedisch', ru: 'Шведский', fr: 'Suédois', es: 'Sueco', cs: 'Švédština', sk: 'Švédčina', it: 'Svedese' },
    { code: 'no', slo: 'Norvežьsky', pl: 'Norweski', en: 'Norwegian', de: 'Norwegisch', ru: 'Норвеžский', fr: 'Norvégien', es: 'Noruego', cs: 'Norština', sk: 'Nórština', it: 'Norvegese' },
    { code: 'fi', slo: 'Finьsky', pl: 'Fiński', en: 'Finnish', de: 'Finnisch', ru: 'Финский', fr: 'Finnois', es: 'Finlandés', cs: 'Finština', sk: 'Fínčina', it: 'Finlandese' },
    { code: 'et', slo: 'Estonьsky', pl: 'Estoński', en: 'Estonian', de: 'Estnisch', ru: 'Эстонский', fr: 'Estonien', es: 'Estonio', cs: 'Estonština', sk: 'Estónčina', it: 'Estone' },
    { code: 'lv', slo: 'Latyšьsky', pl: 'Łotewski', en: 'Latvian', de: 'Lettisch', ru: 'Латышский', fr: 'Letton', es: 'Letón', cs: 'Lotyština', sk: 'Lotyština', it: 'Lettone' },
    { code: 'lt', slo: 'Litovьsky', pl: 'Litewski', en: 'Lithuanian', de: 'Litauisch', ru: 'Литовский', fr: 'Lituanien', es: 'Lituano', cs: 'Litevština', sk: 'Litovčina', it: 'Lituano' },
    { code: 'el', slo: 'Grečьsky', pl: 'Grecki', en: 'Greek', de: 'Griechisch', ru: 'Греческий', fr: 'Grec', es: 'Griego', cs: 'Řečtina', sk: 'Gréčtina', it: 'Greco' },
    { code: 'tr', slo: 'Turečьsky', pl: 'Turecki', en: 'Turkish', de: 'Türkisch', ru: 'Турецкий', fr: 'Turc', es: 'Turco', cs: 'Turečtina', sk: 'Turečtina', it: 'Turco' },
    { code: 'hu', slo: 'Ǫgrinьsky', pl: 'Węgierski', en: 'Hungarian', de: 'Ungarisch', ru: 'Венгерский', fr: 'Hongrois', es: 'Húngaro', cs: 'Maďarština', sk: 'Maďarčina', it: 'Ungherese' },
    { code: 'ro', slo: "Rumunьsky", pl: 'Rumuński', en: 'Romanian', de: 'Rumänisch', ru: 'Румынский', fr: 'Roumain', es: 'Rumano', cs: 'Rumunština', sk: 'Rumunčina', it: 'Rumeno' },
    { code: 'ja', slo: 'Japonьsky', pl: 'Japoński', en: 'Japanese', de: 'Japanisch', ru: 'Японский', fr: 'Japonais', es: 'Japonés', cs: 'Japonština', sk: 'Japončina', it: 'Giapponese' },
    { code: 'ko', slo: 'Koreanьsky', pl: 'Koreański', en: 'Korean', de: 'Koreanisch', ru: 'Корейский', fr: 'Coréen', es: 'Coreano', cs: 'Korejština', sk: 'Korejčina', it: 'Coreano' },
    { code: 'zh-CN', slo: 'Kitajьsky (Uproščeny)', pl: 'Chiński (upr.)', en: 'Chinese (Simp.)', de: 'Chinesisch (Ver.)', ru: 'Китайский', fr: 'Chinois', es: 'Chino', cs: 'Čínština', sk: 'Čínština', it: 'Cinese' },
    { code: 'ar', slo: 'Arabьsky', pl: 'Arabski', en: 'Arabic', de: 'Arabisch', ru: 'Арабский', fr: 'Arabe', es: 'Árabe', cs: 'Arabština', sk: 'Arabština', it: 'Arabo' },
    { code: 'hi', slo: 'Hindьsky', pl: 'Hindi', en: 'Hindi', de: 'Hindi', ru: 'Хинди', fr: 'Hindi', es: 'Hindi', cs: 'Hindština', sk: 'Hindčina', it: 'Hindi' },
    { code: 'id', slo: 'Indonezijьsky', pl: 'Indonezyjski', en: 'Indonesian', de: 'Indonesisch', ru: 'Индонезийский', fr: 'Indonésien', es: 'Indonesio', cs: 'Indonéština', sk: 'Indonézština', it: 'Indonesiano' },
    { code: 'vi', slo: 'Větnamьsky', pl: 'Wietnamski', en: 'Vietnamese', de: 'Vietnamesisch', ru: 'Вьетнамский', fr: 'Vietnamien', es: 'Vietnamita', cs: 'Vietnamština', sk: 'Vietnamčina', it: 'Vietnamita' },
    { code: 'th', slo: 'Tajьsky', pl: 'Tajski', en: 'Thai', de: 'Thailändisch', ru: 'Тайский', fr: 'Thaïlandais', es: 'Tailandés', cs: 'Thajština', sk: 'Thajčina', it: 'Tailandese' },
    { code: 'he', slo: 'Hebrějskьsky', pl: 'Hebrajski', en: 'Hebrew', de: 'Hebräisch', ru: 'Иврит', fr: 'Hébreu', es: 'Hebreo', cs: 'Hebrejština', sk: 'Hebrejčina', it: 'Ebraico' },
    { code: 'az', slo: "Azerbed'ěnьsky", pl: 'Azerbejdżański', en: 'Azerbaijani', de: 'Aserbaidschanisch', ru: 'Азербайджанский', fr: 'Azerbaïdjanais', es: 'Azerbaiyano', cs: 'Ázerbájdžánština', sk: 'Azerbajdžančina', it: 'Azerbaigiano' },
    { code: 'ka', slo: 'Gruzinьsky', pl: 'Gruziński', en: 'Georgian', de: 'Georgisch', ru: 'Грузинский', fr: 'Géorgien', es: 'Georgiano', cs: 'Gruzínština', sk: 'Gruzínčina', it: 'Georgiano' },
    { code: 'hy', slo: 'Armenьsky', pl: 'Ormiański', en: 'Armenian', de: 'Armenisch', ru: 'Армянский', fr: 'Arménien', es: 'Armenio', cs: 'Arménština', sk: 'Arménčina', it: 'Armeno' },
    { code: 'af', slo: 'Južьnozemьsky', pl: 'Afrikaans', en: 'Afrikaans', de: 'Afrikaans', ru: 'Африкаанс', fr: 'Afrikaans', es: 'Afrikaans', cs: 'Afrikánština', sk: 'Afrikánčina', it: 'Afrikaans' },
    { code: 'sq', slo: 'Albanьsky', pl: 'Albański', en: 'Albanian', de: 'Albanisch', ru: 'Албанский', fr: 'Albanais', es: 'Albanés', cs: 'Albánština', sk: 'Albánčina', it: 'Albanese' },
    { code: 'am', slo: 'Amharьsky', pl: 'Amharski', en: 'Amharic', de: 'Amharisch', ru: 'Амхарский', fr: 'Amharique', es: 'Amhárico', cs: 'Amharština', sk: 'Amharčina', it: 'Amarico' },
    { code: 'bn', slo: 'Bengalьsky', pl: 'Bengalski', en: 'Bengali', de: 'Bengalisch', ru: 'Бенгальский', fr: 'Bengali', es: 'Bengalí', cs: 'Bengálština', sk: 'Bengálčina', it: 'Bengalese' },
    { code: 'ms', slo: 'Malajьsky', pl: 'Malajski', en: 'Malay', de: 'Malaiisch', ru: 'Малайский', fr: 'Malais', es: 'Malayo', cs: 'Malajština', sk: 'Malajčina', it: 'Malese' },
    { code: 'zu', slo: 'Zulu', pl: 'Zuluski', en: 'Zulu', de: 'Zulu', ru: 'Зулу', fr: 'Zoulou', es: 'Zulú', cs: 'Zuluština', sk: 'Zuluština', it: 'Zulu' }
];

const uiTranslations = {
    // Twoje oryginalne (bez zmian)
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." },
    de: { title: "Slovo Übersetzer", from: "Von:", to: "Nach:", paste: "Einfügen", clear: "Löschen", copy: "Kopieren", placeholder: "Text eingeben..." },
    fr: { title: "Traducteur Slovo", from: "De :", to: "Vers :", paste: "Coller", clear: "Effacer", copy: "Copier", placeholder: "Entrez le texte..." },
    es: { title: "Traductor Slovo", from: "De:", to: "A:", paste: "Pegar", clear: "Borrar", copy: "Copiar", placeholder: "Escribe texto..." },
    it: { title: "Traduttore Slovo", from: "Da:", to: "A:", paste: "Incolla", clear: "Cancella", copy: "Copia", placeholder: "Inserisci tekst..." },
    pt: { title: "Tradutor Slovo", from: "De:", to: "Para:", paste: "Colar", clear: "Limpar", copy: "Copiar", placeholder: "Digite o texto..." },
    nl: { title: "Slovo Vertaler", from: "Van:", to: "Naar:", paste: "Plakken", clear: "Wissen", copy: "Kopiëren", placeholder: "Voer tekst in..." },
    sv: { title: "Slovo Översättare", from: "Från:", to: "Till:", paste: "Klistra in", clear: "Rensa", copy: "Kopiera", placeholder: "Skriv text..." },
    no: { title: "Slovo Oversetter", from: "Fra:", to: "Till:", paste: "Lim inn", clear: "Fjern", copy: "Kopier", placeholder: "Skriv tekst..." },
    da: { title: "Slovo Oversætter", from: "Fra:", to: "Til:", paste: "Indsæt", clear: "Ryd", copy: "Kopiér", placeholder: "Indtast tekst..." },
    fi: { title: "Slovo Kääntäjä", from: "Lähde:", to: "Kohde:", paste: "Liitä", clear: "Tyhjennä", copy: "Kopioi", placeholder: "Kirjoita teksti..." },
    ru: { title: "Slovo Переводчик", from: "С языка:", to: "На язык:", paste: "Вставить", clear: "Очистить", copy: "Копировать", placeholder: "Введите текст..." },
    uk: { title: "Slovo Перекладач", from: "З мови:", to: "На мову:", paste: "Вставити", clear: "Очистіть", copy: "Копіювати", placeholder: "Введіть текст..." },
    cs: { title: "Slovo Překladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložit", clear: "Vymazat", copy: "Kopírovat", placeholder: "Zadejte text..." },
    sk: { title: "Slovo Prekladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložiť", clear: "Vymazať", copy: "Kopírovať", placeholder: "Zadajte text..." },
    sl: { title: "Slovo Prevajalnik", from: "Iz:", to: "V:", paste: "Prilepi", clear: "Počisti", copy: "Kopiraj", placeholder: "Vnesi besedilo..." },
    hr: { title: "Slovo Prevoditelj", from: "Iz:", to: "U:", paste: "Zalijepi", clear: "Obriši", copy: "Kopiraj", placeholder: "Unesi tekst..." },
    sr: { title: "Slovo Преводилац", from: "Са:", to: "На:", paste: "Налепи", clear: "Обриши", copy: "Копирај", placeholder: "Унеси текст..." },
    bg: { title: "Slovo Преводач", from: "От:", to: "На:", paste: "Постави", clear: "Изчисти", copy: "Копирай", placeholder: "Въведи текст..." },
    tr: { title: "Slovo Çevirici", from: "Dilden:", to: "Dile:", paste: "Yapıştır", clear: "Temizle", copy: "Kopyala", placeholder: "Metin gir..." },
    el: { title: "Slovo Μεταφραστής", from: "Από:", to: "Προς:", paste: "Επικόλληση", clear: "Καθαρισμός", copy: "Αντιγραφή", placeholder: "Εισάγετε κείμενο..." },
    ro: { title: "Traducător Slovo", from: "Din:", to: "În:", paste: "Lipește", clear: "Șterge", copy: "Copiază", placeholder: "Introdu text..." },
    hu: { title: "Slovo Fordító", from: "Erről:", to: "Erre:", paste: "Beillesztés", clear: "Törlés", copy: "Másolás", placeholder: "Írj szöveget..." },
    zh: { title: "Slovo 翻译器", from: "从:", to: "到:", paste: "粘贴", clear: "清除", copy: "复制", placeholder: "输入文本..." },
    ja: { title: "Slovo 翻訳", from: "元の言語:", to: "翻訳先:", paste: "貼り付け", clear: "クリア", copy: "コピー", placeholder: "テキストを入力..." },
    ko: { title: "Slovo 번역기", from: "출발:", to: "도착:", paste: "붙여넣기", clear: "지우기", copy: "복사", placeholder: "텍스트 입력..." },
    ar: { title: "مترجم Slovo", from: "من:", to: "إلى:", paste: "لصق", clear: "مسح", copy: "نسخ", placeholder: "أدخل النص..." },

    // Nowe tłumaczenia interfejsu dla pozostałych języków z Twojej listy:
    af: { title: "Slovo Vertaler", from: "Van taal:", to: "Na taal:", paste: "Plak", clear: "Vee uit", copy: "Kopieer", placeholder: "Tik hier..." },
    sq: { title: "Slovo Përkthyesi", from: "Nga gjuha:", to: "Në gjuhën:", paste: "Ngjit", clear: "Pastro", copy: "Kopjo", placeholder: "Shkruaj këtu..." },
    am: { title: "Slovo አስተርጓሚ", from: "ከቋንቋ:", to: "ወደ ቋንቋ:", paste: "ለጥፍ", clear: "አጽዳ", copy: "ቅዳ", placeholder: "እዚህ ይፃፉ..." },
    az: { title: "Slovo Tərcüməçi", from: "Dildən:", to: "Dilə:", paste: "Yapışdır", clear: "Təmizlə", copy: "Kopyala", placeholder: "Bura yazın..." },
    bn: { title: "Slovo অনুবাদক", from: "ভাষা থেকে:", to: "ভাষা পর্যন্ত:", paste: "পেস্ট", clear: "পরিষ্কার", copy: "কপি", placeholder: "এখানে লিখুন..." },
    ca: { title: "Traductor Slovo", from: "De la llengua:", to: "A la llengua:", paste: "Enganxa", clear: "Neteja", copy: "Copia", placeholder: "Escriu aquí..." },
    et: { title: "Slovo Tõlkija", from: "Keelest:", to: "Keelde:", paste: "Kleebi", clear: "Puhasta", copy: "Kopeeri", placeholder: "Sisesta tekst..." },
    gl: { title: "Tradutor Slovo", from: "Do idioma:", to: "Ao idioma:", paste: "Pegar", clear: "Limpar", copy: "Copiar", placeholder: "Escribe aquí..." },
    hi: { title: "Slovo अनुवादक", from: "भाषा से:", to: "भाषा तक:", paste: "पेस्ट करें", clear: "साफ़ करें", copy: "कॉपी करें", placeholder: "यहाँ लिखें..." },
    id: { title: "Penerjemah Slovo", from: "Dari bahasa:", to: "Ke bahasa:", paste: "Tempel", clear: "Bersihkan", copy: "Salin", placeholder: "Ketik di sini..." },
    ga: { title: "Slovo Aistritheoir", from: "Ó theanga:", to: "Go teanga:", paste: "Greamaigh", clear: "Glan", copy: "Cóipeáil", placeholder: "Scríobh anseo..." },
    lv: { title: "Slovo Tulkotājs", from: "No valodas:", to: "Uz valodu:", paste: "Ielīmēt", clear: "Notīrīt", copy: "Kopēt", placeholder: "Ievadiet tekstu..." },
    lt: { title: "Slovo Vertėjas", from: "Iš kalbos:", to: "Į kalbą:", paste: "Įklijuoti", clear: "Išvalyti", copy: "Kopijuoti", placeholder: "Įveskite tekstą..." },
    ms: { title: "Penterjemah Slovo", from: "Daripada bahasa:", to: "Kepada bahasa:", paste: "Tampal", clear: "Padam", copy: "Salin", placeholder: "Taip di sini..." },
    vi: { title: "Slovo Phiên dịch", from: "Từ ngôn ngữ:", to: "Sang ngôn ngữ:", paste: "Dán", clear: "Xóa", copy: "Sao chép", placeholder: "Nhập văn bản..." }
};

// --- FUNKCJE WIELKOŚCI LITER ---

function getCase(word) {
    if (!word) return "lower";
    if (word === word.toUpperCase() && word.length > 1) return "upper";
    if (word[0] === word[0].toUpperCase()) return "title";
    return "lower";
}

function applyCase(word, caseType) {
    if (!word) return "";
    switch (caseType) {
        case "upper": return word.toUpperCase();
        case "title": return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        default: return word.toLowerCase();
    }
}

// --- LOGIKA TŁUMACZENIA ---

function dictReplace(text, dict) {
    if (!text) return "";
    const urlRegex = /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
    
    let placeholders = [];
    let tempText = text.replace(urlRegex, (match) => {
        placeholders.push(match);
        return `__URL_PH_${placeholders.length - 1}__`;
    });

    tempText = tempText.replace(/[a-ząćęłńóśźżěьъ']+/gi, (word) => {
        const lowWord = word.toLowerCase();
        if (dict[lowWord]) {
            return applyCase(dict[lowWord], getCase(word));
        }
        return word;
    });

    return tempText.replace(/__URL_PH_(\d+)__/g, (match, id) => placeholders[id]);
}

function reorderSmart(text) {
    if (!text) return "";
    const tokens = text.split(/(\s+|[.,!?;:()=+\-%*/]+)/g).filter(t => t !== "" && t !== undefined);
    const result = [];

    for (let i = 0; i < tokens.length; i++) {
        let token = tokens[i];
        let lowToken = token.toLowerCase();

        if (/^[\s.,!?;:()=+\-%*/]+$/.test(token)) {
            result.push(token);
            continue;
        }

        let nextIdx = i + 1;
        while (nextIdx < tokens.length && /^[\s]+$/.test(tokens[nextIdx])) nextIdx++;

        if (nextIdx < tokens.length) {
            let nextToken = tokens[nextIdx];
            let nextLow = nextToken.toLowerCase();

            // Rzeczownik + (Przymiotnik lub Liczebnik)
            if (wordTypes[lowToken] === "noun" && (wordTypes[nextLow] === "adjective" || wordTypes[nextLow] === "numeral")) {
                const firstCase = getCase(token);
                
                // Przymiotnik na przód z wielkością liter pierwotnego pierwszego słowa
                result.push(applyCase(nextToken, firstCase));
                
                // Zachowanie spacji między słowami
                for (let j = i + 1; j < nextIdx; j++) result.push(tokens[j]);
                
                // Rzeczownik na drugie miejsce (małą literą, chyba że pierwotnie był ALL CAPS)
                result.push(firstCase === "upper" ? token.toUpperCase() : token.toLowerCase());
                
                i = nextIdx;
                continue;
            }
        }
        result.push(token);
    }
    return result.join("");
}

async function translate() {
    const input = document.getElementById('userInput');
    const out = document.getElementById('resultOutput');
    if (!input || !out) return;

    const text = input.value;
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;

    if (!text.trim()) { out.innerText = ""; return; }

    try {
        let finalResult = "";
        if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(text, sloToPl);
        } else if (src === 'pl' && tgt === 'slo') {
            let translated = dictReplace(text, plToSlo);
            finalResult = reorderSmart(translated);
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            finalResult = await google(bridge, 'pl', tgt);
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            let translated = dictReplace(bridge, plToSlo);
            finalResult = reorderSmart(translated);
        } else {
            finalResult = await google(text, src, tgt);
        }
        out.innerText = finalResult;
    } catch (e) { out.innerText = "Error..."; }
}

async function google(text, s, t) {
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data[0].map(x => x[0]).join('');
    } catch (e) { return text; }
}

async function loadDictionaries() {
    const status = document.getElementById('dbStatus');
    try {
        const files = ['osnova.json', 'vuzor.json'];
        for (const file of files) {
            const res = await fetch(file);
            if (res.ok) {
                const data = await res.json();
                data.forEach(item => {
                    if (item.polish && item.slovian) {
                        const pl = item.polish.toLowerCase().trim();
                        const slo = item.slovian.toLowerCase().trim();
                        plToSlo[pl] = item.slovian.trim();
                        sloToPl[slo] = item.polish.trim();

                        if (item["type and case"]) {
                            const info = item["type and case"].toLowerCase();
                            if (info.includes("jimenьnik") || info.includes("noun")) wordTypes[slo] = "noun";
                            if (info.includes("priloga") || info.includes("adjective")) wordTypes[slo] = "adjective";
                            if (info.includes("ličьnik") || info.includes("numeral")) wordTypes[slo] = "numeral";
                        }
                    }
                });
            }
        }
        if (status) status.innerText = "Engine Ready.";
    } catch (e) { if (status) status.innerText = "Dict Error."; }
}

async function init() {
    const sysLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[sysLang] ? sysLang : 'en';
    applyUI(uiKey);
    populateLanguageLists(uiKey);

    const savedSrc = localStorage.getItem('srcLang') || (sysLang === 'pl' ? 'pl' : 'en');
    const savedTgt = localStorage.getItem('tgtLang') || 'slo';

    document.getElementById('srcLang').value = savedSrc;
    document.getElementById('tgtLang').value = savedTgt;

    await loadDictionaries();
    document.getElementById('userInput').addEventListener('input', debounce(() => translate(), 300));
}

function applyUI(lang) {
    const ui = uiTranslations[lang] || uiTranslations.en;
    const ids = ['ui-title', 'ui-label-from', 'ui-label-to', 'ui-paste', 'ui-clear', 'ui-copy'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = ui[id.replace('ui-', '')] || "";
    });
    const input = document.getElementById('userInput');
    if (input) input.placeholder = ui.placeholder;
}

function populateLanguageLists(uiLang) {
    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');
    if (!srcSelect || !tgtSelect) return;
    srcSelect.options.length = 0; tgtSelect.options.length = 0;
    languageData.forEach(lang => {
        const name = lang[uiLang] || lang.en;
        srcSelect.add(new Option(name, lang.code));
        tgtSelect.add(new Option(name, lang.code));
    });
}

function swapLanguages() {
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    [src.value, tgt.value] = [tgt.value, src.value];
    localStorage.setItem('srcLang', src.value);
    localStorage.setItem('tgtLang', tgt.value);
    translate();
}

function clearText() {
    document.getElementById('userInput').value = "";
    document.getElementById('resultOutput').innerText = "";
}

function copyText() {
    const text = document.getElementById('resultOutput').innerText;
    navigator.clipboard.writeText(text);
}

async function pasteText() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById('userInput').value = text;
        translate();
    } catch(e) { console.log("Clipboard error"); }
}

function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
}

window.onload = init;
