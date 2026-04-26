let plToSlo = {}, sloToPl = {};
let wordTypes = {};

const languageData = [
    { code: 'slo', slo: 'Slověnьsky', pl: 'Słowiański', en: 'Slovian (Slavic)', de: 'Slawisch', cs: 'Slovanský', sk: 'Slovanský', ru: 'Славянский', fr: 'Slave', es: 'Eslavo', it: 'Slavo', uk: 'Слов\'янська', be: 'Славянская', bg: 'Славянски', hr: 'Slavenski', sr: 'Словенски', 'sr-Latn': 'Slavenski', sl: 'Slovanski', mk: 'Словенски', pt: 'Eslavo', nl: 'Slavisch', da: 'Slavisk', sv: 'Slaviska', no: 'Slavisk', fi: 'Slaavilainen', et: 'Slaavi', lv: 'Slāvu', lt: 'Slavų', el: 'Σλαβική', tr: 'Slavca', hu: 'Szláv', ro: 'Slavă', ja: 'スラヴ語', ko: '슬라브어', "zh-CN": '斯拉夫语', "zh-TW": '斯拉夫語', ar: 'السلافية', hi: 'स्लाविक', id: 'Slavia', vi: 'Tiếng Slav', th: 'ภาษาสลาวิก', he: 'סלאבית', az: 'Slavyan', ka: 'სლავური', hy: 'Սլավոնական', af: 'Slawies', sq: 'Sllave', am: 'ስላቪክ', bn: 'স্লাভিক', ms: 'Slavik', zu: 'IsiSlavic' },
    { code: 'en', pl: 'Angielski', en: 'English', slo: "Angol'ьsky", de: 'Englisch' },
    { code: 'pl', pl: 'Polski', en: 'Polish', slo: "Pol'ьsky", de: 'Polnisch' },
    { code: 'de', pl: 'Niemiecki', en: 'German', slo: 'Nemьčьsky', de: 'Deutsch' },
    { code: 'cs', pl: 'Czeski', en: 'Czech', slo: 'Češьsky', de: 'Tschechisch' },
    { code: 'sk', pl: 'Słowacki', en: 'Slovak', slo: 'Slovačьsky', de: 'Slowakisch' },
    { code: 'ru', pl: 'Rosyjski', en: 'Russian', slo: 'Rusьsky', de: 'Russisch' },
    { code: 'fr', pl: 'Francuski', en: 'French', slo: 'Franьsky', de: 'Französisch' },
    { code: 'es', pl: 'Hiszpański', en: 'Spanish', slo: 'Španьsky', de: 'Spanisch' },
    { code: 'it', pl: 'Włoski', en: 'Italian', slo: 'Volšьsky', de: 'Italienisch' },
    { code: 'uk', pl: 'Ukraiński', en: 'Ukrainian', slo: 'Ukrajinьsky', de: 'Ukrainisch' },
    { code: 'af', pl: 'Afrikaans', en: 'Afrikaans', slo: 'Južьnozemьsky', de: 'Afrikaans' },
    { code: 'sq', pl: 'Albański', en: 'Albanian', slo: 'Albanьsky', de: 'Albanisch' },
    { code: 'am', pl: 'Amharski', en: 'Amharic', slo: 'Amharьsky', de: 'Amharisch' },
    { code: 'ar', pl: 'Arabski', en: 'Arabic', slo: 'Arabьsky', de: 'Arabisch' },
    { code: 'az', pl: 'Azerbejdżański', en: 'Azerbaijani', slo: "Azerbed'ěnьsky", de: 'Aserbaidschanisch' },
    { code: 'bn', pl: 'Bengalski', en: 'Bengali', slo: 'Bengalьsky', de: 'Bengalisch' },
    { code: 'be', pl: 'Białoruski', en: 'Belarusian', slo: 'Bělorusьsky', de: 'Weißrussisch' },
    { code: 'bg', pl: 'Bułgarski', en: 'Bulgarian', slo: "Boulgar'ьsky", de: 'Bulgarisch' },
    { code: 'ca', pl: 'Kataloński', en: 'Catalan', slo: "Katalonьsky", de: 'Katalanisch' },
    { code: 'zh-CN', pl: 'Chiński (uproszczony)', en: 'Chinese (Simplified)', slo: 'Kitajьsky (Uproščeny)', de: 'Chinesisch (Vereinfacht)' },
    { code: 'zh-TW', pl: 'Chiński (tradycyjny)', en: 'Chinese (Traditional)', slo: 'Kitajьsky (Obyčajьny)', de: 'Chinesisch (Traditionell)' },
    { code: 'hr', pl: 'Chorwacki', en: 'Croatian', slo: 'Horvatьsky', de: 'Kroatisch' },
    { code: 'da', pl: 'Duński', en: 'Danish', slo: 'Dunьsky', de: 'Dänisch' },
    { code: 'nl', pl: 'Holenderski', en: 'Dutch', slo: 'Niskozemьsky', de: 'Niederländisch' },
    { code: 'et', pl: 'Estoński', en: 'Estonian', slo: 'Estonьsky', de: 'Estnisch' },
    { code: 'fi', pl: 'Fiński', en: 'Finnish', slo: 'Finьsky', de: 'Finnisch' },
    { code: 'gl', pl: 'Galicyjski', en: 'Galician', slo: 'Galicijьski', de: 'Galizisch' },
    { code: 'el', pl: 'Grecki', en: 'Greek', slo: 'Grečьsky', de: 'Griechisch' },
    { code: 'hi', pl: 'Hindi', en: 'Hindi', slo: 'Hindьsky', de: 'Hindi' },
    { code: 'hu', pl: 'Węgierski', en: 'Hungarian', slo: 'Ǫgrinьsky', de: 'Ungarisch' },
    { code: 'is', pl: 'Islandzki', en: 'Icelandic', slo: 'Ledozemьsky', de: 'Isländisch' },
    { code: 'id', pl: 'Indonezyjski', en: 'Indonesian', slo: 'Indonezijьsky', de: 'Indonesisch' },
    { code: 'ga', pl: 'Irlandzki', en: 'Irish', slo: 'Irьski', de: 'Irisch' },
    { code: 'ja', pl: 'Japoński', en: 'Japanese', slo: 'Japonьsky', de: 'Japanisch' },
    { code: 'ko', pl: 'Koreański', en: 'Korean', slo: 'Koreanьsky', de: 'Koreanisch' },
    { code: 'lv', pl: 'Łotewski', en: 'Latvian', slo: 'Latyšьsky', de: 'Lettisch' },
    { code: 'lt', pl: 'Litewski', en: 'Lithuanian', slo: 'Litovьsky', de: 'Litauisch' },
    { code: 'mk', pl: 'Macedoński', en: 'Macedonian', slo: 'Makedonьsky', de: 'Mazedonisch' },
    { code: 'ms', pl: 'Malajski', en: 'Malay', slo: 'Malajьsky', de: 'Malaiisch' },
    { code: 'no', pl: 'Norweski', en: 'Norwegian', slo: 'Norvežьsky', de: 'Norwegisch' },
    { code: 'pt', pl: 'Portugalski', en: 'Portuguese', slo: "Portugal'ьsky", de: 'Portugiesisch' },
    { code: 'ro', pl: 'Rumuński', en: 'Romanian', slo: "Rumunьsky", de: 'Rumänisch' },
    { code: 'sr', pl: 'Serbski', en: 'Serbian', slo: 'Sirbьsky', de: 'Serbisch' },
    { code: 'sl', pl: 'Słoweński', en: 'Slovenian', slo: 'Slovenečьsky', de: 'Slowenisch' },
    { code: 'sv', pl: 'Szwedzki', en: 'Swedish', slo: 'Švedьsky', de: 'Schwedisch' },
    { code: 'th', pl: 'Tajski', en: 'Thai', slo: 'Tajьsky', de: 'Thailändisch' },
    { code: 'tr', pl: 'Turecki', en: 'Turkish', slo: 'Turečьsky', de: 'Türkisch' },
    { code: 'vi', pl: 'Wietnamski', en: 'Vietnamese', slo: 'Větnamьsky', de: 'Vietnamesisch' }
];

const uiTranslations = {
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." },
    de: { title: "Slovo Übersetzer", from: "Von:", to: "Nach:", paste: "Einfügen", clear: "Löschen", copy: "Kopieren", placeholder: "Text eingeben..." },
    fr: { title: "Traducteur Slovo", from: "De :", to: "Vers :", paste: "Coller", clear: "Effacer", copy: "Copier", placeholder: "Entrez le texte..." },
    es: { title: "Traductor Slovo", from: "De:", to: "A:", paste: "Pegar", clear: "Borrar", copy: "Copier", placeholder: "Escribe texto..." },
    it: { title: "Traduttore Slovo", from: "Da:", to: "A:", paste: "Incolla", clear: "Cancella", copy: "Copia", placeholder: "Inserisci testo..." },
    pt: { title: "Tradutor Slovo", from: "De:", to: "Para:", paste: "Colar", clear: "Limpar", copy: "Copiar", placeholder: "Digite o texto..." },
    nl: { title: "Slovo Vertaler", from: "Van:", to: "Naar:", paste: "Plakken", clear: "Wissen", copy: "Kopiëren", placeholder: "Voer tekst in..." },
    sv: { title: "Slovo Översättare", from: "Från:", to: "Till:", paste: "Klistra in", clear: "Rensa", copy: "Kopiera", placeholder: "Skriv text..." },
    no: { title: "Slovo Oversetter", from: "Fra:", to: "Til:", paste: "Lim inn", clear: "Fjern", copy: "Kopier", placeholder: "Skriv tekst..." },
    da: { title: "Slovo Oversætter", from: "Fra:", to: "Til:", paste: "Indsæt", clear: "Ryd", copy: "Kopiér", placeholder: "Indtast tekst..." },
    fi: { title: "Slovo Kääntäjä", from: "Lähde:", to: "Kohde:", paste: "Liitä", clear: "Tyhjennä", copy: "Kopioi", placeholder: "Kirjoita teksti..." },
    ru: { title: "Slovo Переводчик", from: "С языка:", to: "На язык:", paste: "Вставить", clear: "Очистить", copy: "Копировать", placeholder: "Введите текст..." },
    uk: { title: "Slovo Перекладач", from: "З мови:", to: "На мову:", paste: "Вставити", clear: "Очистити", copy: "Копіювати", placeholder: "Введіть текст..." },
    cs: { title: "Slovo Překladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložit", clear: "Vymazat", copy: "Kopírovat", placeholder: "Zadejte text..." },
    sk: { title: "Slovo Prekladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložiť", clear: "Vymazať", copy: "Kopírovat", placeholder: "Zadajte text..." },
    sl: { title: "Slovo Prevajalnik", from: "Iz:", to: "V:", paste: "Prilepi", clear: "Počisti", copy: "Kopiraj", placeholder: "Vnesi besedilo..." },
    hr: { title: "Slovo Prevoditelj", from: "Iz:", to: "U:", paste: "Zalijepi", clear: "Obriši", copy: "Kopiraj", placeholder: "Unesi tekst..." },
    sr: { title: "Slovo Преводилац", from: "Са језика:", to: "На језик:", paste: "Налепи", clear: "Обриши", copy: "Копирај", placeholder: "Унеси текст..." },
    'sr-Latn': { title: "Slovo Prevodilac", from: "Sa jezika:", to: "Na jezik:", paste: "Nalepi", clear: "Obriši", copy: "Kopiraj", placeholder: "Unesi tekst..." },
    bg: { title: "Slovo Преводач", from: "От:", to: "На:", paste: "Постави", clear: "Изчисти", copy: "Копирай", placeholder: "Въведи текст..." },
    tr: { title: "Slovo Çevirici", from: "Dilden:", to: "Dile:", paste: "Yapıştır", clear: "Temizle", copy: "Kopyala", placeholder: "Metin gir..." },
    el: { title: "Slovo Μεταφραστής", from: "Από:", to: "Προς:", paste: "Επικόλληση", clear: "Καθαρισμός", copy: "Αντιγραφή", placeholder: "Εισάγετε κείμενο..." },
    ro: { title: "Traducător Slovo", from: "Din:", to: "În:", paste: "Lipește", clear: "Șterge", copy: "Copiază", placeholder: "Introdu text..." },
    hu: { title: "Slovo Fordító", from: "Erről:", to: "Erre:", paste: "Beillesztés", clear: "Törlés", copy: "Másolás", placeholder: "Írj szöveget..." },
    zh: { title: "Slovo 翻译器", from: "从:", to: "到:", paste: "粘贴", clear: "清除", copy: "复制", placeholder: "输入文本..." },
    ja: { title: "Slovo 翻訳", from: "元の言語:", to: "翻訳先:", paste: "貼り付け", clear: "クリア", copy: "コピー", placeholder: "テキストを入力..." },
    ko: { title: "Slovo 번역기", from: "출발:", to: "도착:", paste: "붙여넣기", clear: "지우기", copy: "복사", placeholder: "텍스트 입력..." },
    ar: { title: "مترجم Slovo", from: "من:", to: "إلى:", paste: "لصق", clear: "مسح", copy: "نسخ", placeholder: "أدخل النص..." }
};

// --- LOCAL STORAGE + DOMYŚLNY JĘZYK INTERFEJSU I TŁUMACZENIA ---
const STORAGE_KEYS = {
    uiLang: "uiLang",
    uiLangManual: "uiLangManual",
    srcLang: "srcLang",
    tgtLang: "tgtLang"
};

function safeLocalGet(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
}

function safeLocalSet(key, value) {
    try { localStorage.setItem(key, value); } catch (e) {}
}

function getBrowserLocales() {
    const list = [];
    try {
        if (Array.isArray(navigator.languages)) {
            navigator.languages.forEach(l => {
                if (l && !list.includes(l)) list.push(l);
            });
        }
        if (navigator.language && !list.includes(navigator.language)) {
            list.push(navigator.language);
        }
    } catch (e) {}
    if (!list.length) list.push("en");
    return list;
}

function buildLocaleCandidates(locale) {
    const raw = String(locale || "").trim().replace("_", "-");
    if (!raw) return [];

    const lower = raw.toLowerCase();
    const base = lower.split("-")[0];

    if (lower === "zh" || lower.includes("zh-hans") || lower.includes("zh-cn") || lower.includes("zh-sg")) {
        return ["zh-CN", "zh"];
    }

    if (lower.includes("zh-hant") || lower.includes("zh-tw") || lower.includes("zh-hk") || lower.includes("zh-mo")) {
        return ["zh-TW", "zh"];
    }

    if (lower.includes("sr-latn")) {
        return ["sr-Latn", "sr"];
    }

    return [...new Set([raw, lower, base].filter(Boolean))];
}

function findSupportedFromLocales(locales, supportedValues, fallback) {
    const supported = new Set(supportedValues);
    for (const locale of locales) {
        const candidates = buildLocaleCandidates(locale);
        for (const candidate of candidates) {
            if (supported.has(candidate)) return candidate;
        }
    }
    return fallback;
}

function isSupportedLanguageCode(code) {
    return languageData.some(l => l.code === code);
}

function isSupportedUILanguage(code) {
    return !!uiTranslations[code];
}

function getStoredLanguage(key) {
    const value = safeLocalGet(key);
    if (value && isSupportedLanguageCode(value)) return value;
    return null;
}

function getStoredUILanguage() {
    // Interfejs ma się sam dopasowywać do języka przeglądarki/urządzenia.
    // Stary localStorage.uiLang mógł trzymać np. "pl" z wcześniejszych testów,
    // więc używamy go tylko wtedy, gdy język interfejsu został jawnie ustawiony.
    const manual = safeLocalGet(STORAGE_KEYS.uiLangManual);
    if (manual !== "1") return null;

    const value = safeLocalGet(STORAGE_KEYS.uiLang);
    if (value && isSupportedUILanguage(value)) return value;
    return null;
}

function detectDefaultUILanguage() {
    const stored = getStoredUILanguage();
    if (stored) return stored;

    const detected = findSupportedFromLocales(getBrowserLocales(), Object.keys(uiTranslations), "en");
    return detected || "en";
}

function detectDefaultSourceLanguage() {
    const stored = getStoredLanguage(STORAGE_KEYS.srcLang);
    if (stored) return stored;

    const detected = findSupportedFromLocales(getBrowserLocales(), languageData.map(l => l.code), "pl");
    return detected === "slo" ? "pl" : detected;
}

function detectDefaultTargetLanguage(srcLang) {
    const stored = getStoredLanguage(STORAGE_KEYS.tgtLang);
    if (stored && stored !== srcLang) return stored;
    return srcLang === "slo" ? "pl" : "slo";
}

function getDisplayLocale(uiLang) {
    const locales = getBrowserLocales();

    if (uiLang === "zh") {
        const chinese = locales.find(l => String(l).toLowerCase().startsWith("zh"));
        return chinese || "zh-CN";
    }

    if (uiLang === "sr-Latn") return "sr-Latn";

    // Intl.DisplayNames powinien dostać język interfejsu, nie zawsze pierwszy język systemu.
    // Dzięki temu niemiecki interfejs pokazuje Deutsch/Polnisch/Slawisch, a nie polskie nazwy.
    return uiLang || locales[0] || "en";
}

function normalizeSelectPair(src, tgt) {
    let source = isSupportedLanguageCode(src) ? src : "pl";
    let target = isSupportedLanguageCode(tgt) ? tgt : "slo";

    if (source === target) {
        target = source === "slo" ? "pl" : "slo";
    }

    return { source, target };
}

function populateLanguageLists(uiLang, userLocale) {
    const s1 = document.getElementById('srcLang');
    const s2 = document.getElementById('tgtLang');
    if (!s1 || !s2) return;

    const oldSrc = s1.value;
    const oldTgt = s2.value;

    let dn;
    try {
        dn = new Intl.DisplayNames([userLocale || getDisplayLocale(uiLang)], { type: 'language' });
    } catch (e) {
        dn = null;
    }

    [s1, s2].forEach(select => {
        select.options.length = 0;

        languageData.forEach(lang => {
            let name = "";

            if (lang.code === "slo") {
                // Tu specjalnie nie używamy Intl.DisplayNames, bo "slo" to język projektu.
                // Dla niemieckiego ma być: Slawisch.
                name = lang[uiLang] || (uiLang === "zh" ? lang["zh-CN"] : "") || lang.en || lang.slo || lang.code;
            } else if (dn) {
                try {
                    name = dn.of(lang.code);
                } catch (e) {
                    name = lang[uiLang] || (uiLang === "zh" ? lang["zh-CN"] : "") || lang.en || lang.code;
                }
            } else {
                name = lang[uiLang] || (uiLang === "zh" ? lang["zh-CN"] : "") || lang.en || lang.code;
            }

            if (!name) name = lang.code;
            name = name.charAt(0).toUpperCase() + name.slice(1);
            select.add(new Option(name, lang.code));
        });
    });

    if (oldSrc && isSupportedLanguageCode(oldSrc)) s1.value = oldSrc;
    if (oldTgt && isSupportedLanguageCode(oldTgt)) s2.value = oldTgt;
}

function applyUI(lang) {
    const uiLang = uiTranslations[lang] ? lang : "en";
    const ui = uiTranslations[uiLang] || uiTranslations.en;

    const idToKey = {
        "ui-title": "title",
        "ui-label-from": "from",
        "ui-label-to": "to",
        "ui-paste": "paste",
        "ui-clear": "clear",
        "ui-copy": "copy"
    };

    Object.keys(idToKey).forEach(id => {
        const el = document.getElementById(id);
        const key = idToKey[id];
        if (el && ui[key]) el.innerText = ui[key];
    });

    const input = document.getElementById("userInput");
    if (input && ui.placeholder) input.placeholder = ui.placeholder;

    if (ui.title) document.title = ui.title;

    const html = document.documentElement;
    if (html) {
        html.lang = uiLang === "slo" ? "sla" : uiLang;
        html.dir = uiLang === "ar" ? "rtl" : "ltr";
    }
}

function setInterfaceLanguage(lang) {
    if (!isSupportedUILanguage(lang)) return;

    safeLocalSet(STORAGE_KEYS.uiLang, lang);
    safeLocalSet(STORAGE_KEYS.uiLangManual, "1");

    const displayLocale = getDisplayLocale(lang);
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    const currentSrc = src ? src.value : null;
    const currentTgt = tgt ? tgt.value : null;

    applyUI(lang);
    populateLanguageLists(lang, displayLocale);

    if (src && currentSrc && isSupportedLanguageCode(currentSrc)) src.value = currentSrc;
    if (tgt && currentTgt && isSupportedLanguageCode(currentTgt)) tgt.value = currentTgt;
}

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
        if (dict[lowWord]) return applyCase(dict[lowWord], getCase(word));
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

        if (wordTypes[lowToken]) {
            let group = [];
            let currentIdx = i;
            let firstWordCase = getCase(tokens[i]);

            while (currentIdx < tokens.length) {
                let currentToken = tokens[currentIdx];
                let currentLow = currentToken.toLowerCase();

                if (/^[\s]+$/.test(currentToken)) {
                    currentIdx++;
                    continue;
                }

                let type = wordTypes[currentLow];
                if (type === "noun" || type === "adjective" || type === "numeral") {
                    group.push({ val: currentToken, type: type });
                    i = currentIdx;
                    currentIdx++;
                } else {
                    break;
                }
            }

            if (group.length > 1) {
                const order = { "numeral": 1, "adjective": 2, "noun": 3 };
                group.sort((a, b) => (order[a.type] || 99) - (order[b.type] || 99));

                group.forEach((word, index) => {
                    let formattedWord = word.val.toLowerCase();
                    if (index === 0) formattedWord = applyCase(word.val, firstWordCase);
                    else if (firstWordCase === "upper") formattedWord = word.val.toUpperCase();
                    result.push(formattedWord);
                    if (index < group.length - 1) result.push(" ");
                });
                continue;
            } else if (group.length === 1) {
                result.push(token);
                continue;
            }
        }

        result.push(token);
    }
    return fixDisplaySpacing(result.join(""));
}

function fixDisplaySpacing(text) {
    return String(text ?? "")
        .replace(/\s+([,.;:!?%])/g, "$1")
        .replace(/([([{„«])\s+/g, "$1")
        .replace(/\s+([)\]}”»])/g, "$1")
        .replace(/\s*—\s*/g, " — ")
        .replace(/([\p{L}\p{M}0-9ьъěęǫšžčćńłóśźż])\s*-\s*([\p{L}\p{M}0-9ьъěęǫšžčćńłóśźż])/gu, "$1 - $2")
        .replace(/\s+/g, " ")
        .trim();
}

// --- GOOGLE + KOREKTA WEJŚCIA ---
const ENABLE_GOOGLE_INPUT_CORRECTION = true;
const AUTO_USE_GOOGLE_CORRECTION = true;
const correctionCache = new Map();
let lastCorrectionKey = "";

function normalizeCorrectionCompare(text) {
    return String(text || "")
        .normalize("NFC")
        .replace(/[“”„]/g, '"')
        .replace(/[’]/g, "'")
        .replace(/\s+/g, " ")
        .trim()
        .toLocaleLowerCase("pl");
}

function shouldCorrectInput(text, src, tgt) {
    if (!ENABLE_GOOGLE_INPUT_CORRECTION) return false;
    if (!text || !text.trim()) return false;
    if (src === "slo") return false;
    if (text.trim().length < 4) return false;
    return true;
}

const LOCAL_CORRECTION_MAX_DISTANCE = 2;
const LOCAL_CORRECTION_MIN_WORD_LENGTH = 4;
const localCorrectionIndexCache = new Map();

function getLocalCorrectionDict(src) {
    try {
        if (src === "pl" && typeof plToSlo !== "undefined") return plToSlo || {};
        if (src === "slo" && typeof sloToPl !== "undefined") return sloToPl || {};
    } catch (e) {}
    return null;
}

function buildLocalCorrectionIndex(src) {
    const cacheKey = src;
    if (localCorrectionIndexCache.has(cacheKey)) return localCorrectionIndexCache.get(cacheKey);

    const dict = getLocalCorrectionDict(src);
    const index = new Map();

    if (!dict) {
        localCorrectionIndexCache.set(cacheKey, index);
        return index;
    }

    Object.keys(dict).forEach(function (word) {
        const w = normalizeCorrectionCompare(word);
        if (!w || w.length < LOCAL_CORRECTION_MIN_WORD_LENGTH) return;
        if (!/^[\p{L}\p{M}0-9'’]+$/u.test(w)) return;
        const first = Array.from(w)[0] || "";
        const len = Array.from(w).length;
        const key = first + "|" + len;
        if (!index.has(key)) index.set(key, []);
        index.get(key).push(w);
    });

    localCorrectionIndexCache.set(cacheKey, index);
    return index;
}

function levenshteinLimited(a, b, limit) {
    const aa = Array.from(a);
    const bb = Array.from(b);
    if (Math.abs(aa.length - bb.length) > limit) return limit + 1;
    if (a === b) return 0;

    let prev = new Array(bb.length + 1);
    let curr = new Array(bb.length + 1);
    for (let j = 0; j <= bb.length; j++) prev[j] = j;

    for (let i = 1; i <= aa.length; i++) {
        curr[0] = i;
        let rowMin = curr[0];
        for (let j = 1; j <= bb.length; j++) {
            const cost = aa[i - 1] === bb[j - 1] ? 0 : 1;
            curr[j] = Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost);
            if (curr[j] < rowMin) rowMin = curr[j];
        }
        if (rowMin > limit) return limit + 1;
        [prev, curr] = [curr, prev];
    }
    return prev[bb.length];
}

function applyOriginalWordCase(original, corrected) {
    const raw = String(original || "");
    const c = String(corrected || "");
    if (!c) return c;
    if (raw.length > 1 && raw === raw.toLocaleUpperCase("pl")) return c.toLocaleUpperCase("pl");
    if (raw[0] && raw[0] === raw[0].toLocaleUpperCase("pl") && raw[0] !== raw[0].toLocaleLowerCase("pl")) {
        return c.charAt(0).toLocaleUpperCase("pl") + c.slice(1);
    }
    return c;
}

function findClosestLocalWord(word, src) {
    const dict = getLocalCorrectionDict(src);
    if (!dict) return null;

    const normalized = normalizeCorrectionCompare(word);
    if (!normalized || normalized.length < LOCAL_CORRECTION_MIN_WORD_LENGTH) return null;
    if (Object.prototype.hasOwnProperty.call(dict, normalized)) return null;
    if (!/^[\p{L}\p{M}0-9'’]+$/u.test(normalized)) return null;

    const chars = Array.from(normalized);
    const first = chars[0] || "";
    const len = chars.length;
    const index = buildLocalCorrectionIndex(src);

    let best = null;
    let bestDist = LOCAL_CORRECTION_MAX_DISTANCE + 1;

    for (let l = len - LOCAL_CORRECTION_MAX_DISTANCE; l <= len + LOCAL_CORRECTION_MAX_DISTANCE; l++) {
        const candidates = index.get(first + "|" + l) || [];
        for (const candidate of candidates) {
            const dist = levenshteinLimited(normalized, candidate, LOCAL_CORRECTION_MAX_DISTANCE);
            if (dist < bestDist) {
                bestDist = dist;
                best = candidate;
                if (dist === 1) break;
            }
        }
        if (bestDist === 1) break;
    }

    if (!best || bestDist > LOCAL_CORRECTION_MAX_DISTANCE) return null;
    return applyOriginalWordCase(word, best);
}

function localCorrectText(text, src) {
    const original = String(text || "");
    if (src !== "pl") return original;
    const tokens = original.match(/([\p{L}\p{M}0-9'’]+|\s+|[^\s\p{L}\p{M}0-9'’]+)/gu) || [original];
    let changed = false;
    const correctedTokens = tokens.map(function (token) {
        if (!/^[\p{L}\p{M}0-9'’]+$/u.test(token)) return token;
        const corrected = findClosestLocalWord(token, src);
        if (corrected && normalizeCorrectionCompare(corrected) !== normalizeCorrectionCompare(token)) {
            changed = true;
            return corrected;
        }
        return token;
    });
    return changed ? correctedTokens.join("") : original;
}

async function googleRaw(text, s, t) {
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url);
        const data = await res.json();
        if (!Array.isArray(data) || !Array.isArray(data[0])) return text;
        return data[0].map(x => Array.isArray(x) ? (x[0] || "") : "").join('');
    } catch (e) {
        console.warn("Google error:", e);
        return text;
    }
}

async function google(text, s, t) {
    return await googleRaw(text, s, t);
}

function withTimeout(promise, ms, fallback) {
    return Promise.race([
        promise,
        new Promise(resolve => setTimeout(() => resolve(fallback), ms))
    ]);
}

async function getGoogleCorrectedInput(text, lang) {
    const original = String(text || "");
    const key = `${lang}::${original}`;
    if (correctionCache.has(key)) return correctionCache.get(key);

    let corrected = localCorrectText(original, lang);
    if (lang === "pl") {
        correctionCache.set(key, corrected);
        return corrected;
    }

    if (normalizeCorrectionCompare(corrected) === normalizeCorrectionCompare(original)) {
        corrected = await withTimeout(googleRaw(original, lang, lang), 900, original);
        if (!corrected || !corrected.trim()) corrected = original;
    }

    if (normalizeCorrectionCompare(corrected) === normalizeCorrectionCompare(original)) {
        const autoCorrected = await withTimeout(googleRaw(original, "auto", lang), 900, original);
        if (autoCorrected && autoCorrected.trim()) corrected = autoCorrected;
    }

    correctionCache.set(key, corrected);
    return corrected;
}

function ensureCorrectionBox() {
    let box = document.getElementById("correctionSuggestionBox");
    if (box) return box;

    const input = document.getElementById("userInput");
    if (!input || !input.parentNode) return null;

    box = document.createElement("div");
    box.id = "correctionSuggestionBox";
    box.style.display = "none";
    box.style.margin = "8px 0 10px 0";
    box.style.padding = "10px 12px";
    box.style.border = "1px solid #d7e3ff";
    box.style.borderRadius = "12px";
    box.style.background = "#f4f8ff";
    box.style.color = "#1f2937";
    box.style.fontSize = "14px";
    box.style.lineHeight = "1.4";
    input.insertAdjacentElement("afterend", box);
    return box;
}

function hideCorrectionSuggestion() {
    const box = document.getElementById("correctionSuggestionBox");
    if (box) {
        box.style.display = "none";
        box.innerHTML = "";
    }
    lastCorrectionKey = "";
}

function showCorrectionSuggestion(original, corrected, lang) {
    const box = ensureCorrectionBox();
    if (!box) return;

    const key = `${lang}::${original}::${corrected}`;
    if (lastCorrectionKey === key) return;
    lastCorrectionKey = key;

    box.innerHTML = "";

    const label = document.createElement("span");
    label.textContent = "Sugestia poprawy: ";

    const suggestion = document.createElement("button");
    suggestion.type = "button";
    suggestion.textContent = corrected;
    suggestion.style.border = "none";
    suggestion.style.background = "transparent";
    suggestion.style.color = "#0b63ff";
    suggestion.style.fontWeight = "600";
    suggestion.style.cursor = "pointer";
    suggestion.style.padding = "0 4px";

    const useCorrection = function () {
        const input = document.getElementById("userInput");
        if (input) {
            input.value = corrected;
            hideCorrectionSuggestion();
            translate();
        }
    };

    suggestion.onclick = useCorrection;

    const useBtn = document.createElement("button");
    useBtn.type = "button";
    useBtn.textContent = "Użyj";
    useBtn.style.marginLeft = "10px";
    useBtn.style.padding = "4px 10px";
    useBtn.style.border = "1px solid #0b63ff";
    useBtn.style.borderRadius = "8px";
    useBtn.style.background = "#ffffff";
    useBtn.style.color = "#0b63ff";
    useBtn.style.cursor = "pointer";
    useBtn.style.fontWeight = "600";
    useBtn.onclick = useCorrection;

    const ignoreBtn = document.createElement("button");
    ignoreBtn.type = "button";
    ignoreBtn.textContent = "Ignoruj";
    ignoreBtn.style.marginLeft = "6px";
    ignoreBtn.style.padding = "4px 10px";
    ignoreBtn.style.border = "1px solid #d1d5db";
    ignoreBtn.style.borderRadius = "8px";
    ignoreBtn.style.background = "#ffffff";
    ignoreBtn.style.color = "#374151";
    ignoreBtn.style.cursor = "pointer";
    ignoreBtn.onclick = hideCorrectionSuggestion;

    box.appendChild(label);
    box.appendChild(suggestion);
    box.appendChild(useBtn);
    box.appendChild(ignoreBtn);
    box.style.display = "block";
}

async function prepareInputForTranslation(text, src, tgt) {
    const original = String(text || "");

    if (!shouldCorrectInput(original, src, tgt)) {
        hideCorrectionSuggestion();
        return { text: original, corrected: false, suggestion: original };
    }

    const corrected = await getGoogleCorrectedInput(original, src);

    if (corrected && normalizeCorrectionCompare(corrected) !== normalizeCorrectionCompare(original)) {
        showCorrectionSuggestion(original, corrected, src);
        return {
            text: AUTO_USE_GOOGLE_CORRECTION ? corrected : original,
            corrected: true,
            suggestion: corrected
        };
    }

    hideCorrectionSuggestion();
    return { text: original, corrected: false, suggestion: original };
}

async function translate() {
    const input = document.getElementById('userInput');
    const out = document.getElementById('resultOutput');
    if (!input || !out) return;

    const originalText = input.value;
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;

    if (!originalText.trim()) {
        out.innerText = "";
        hideCorrectionSuggestion();
        return;
    }

    try {
        let finalResult = "";
        const prepared = await prepareInputForTranslation(originalText, src, tgt);
        const text = prepared.text;

        if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(originalText, sloToPl);
        } else if (src === 'pl' && tgt === 'slo') {
            let translated = dictReplace(text, plToSlo);
            finalResult = reorderSmart(translated);
        } else if (src === 'slo') {
            const bridge = dictReplace(originalText, sloToPl);
            finalResult = await google(bridge, 'pl', tgt);
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            let translated = dictReplace(bridge, plToSlo);
            finalResult = reorderSmart(translated);
        } else {
            finalResult = await google(text, src, tgt);
        }

        out.innerText = fixDisplaySpacing(finalResult);
    } catch (e) {
        console.error(e);
        out.innerText = "Error...";
    }
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
                            if (info.includes("jimenьnik") || info.includes("imenьnik") || info.includes("noun") || info.includes("rzeczownik")) {
                                wordTypes[slo] = "noun";
                            }
                            if (info.includes("priloga") || info.includes("pridavьnik") || info.includes("pridavnik") || info.includes("adjective") || info.includes("przymiotnik")) {
                                wordTypes[slo] = "adjective";
                            }
                            if (info.includes("ličьnik") || info.includes("ličebьnik") || info.includes("liczebnik") || info.includes("numeral")) {
                                wordTypes[slo] = "numeral";
                            }
                        }
                    }
                });
            }
        }
        if (status) status.innerText = "Engine Ready.";
    } catch (e) {
        console.error(e);
        if (status) status.innerText = "Dict Error.";
    }
}

async function init() {
    const uiKey = detectDefaultUILanguage();
    const displayLocale = getDisplayLocale(uiKey);

    applyUI(uiKey);
    populateLanguageLists(uiKey, displayLocale);

    const defaultSrc = detectDefaultSourceLanguage();
    const defaultTgt = detectDefaultTargetLanguage(defaultSrc);
    const pair = normalizeSelectPair(defaultSrc, defaultTgt);

    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');

    if (srcSelect) srcSelect.value = pair.source;
    if (tgtSelect) tgtSelect.value = pair.target;

    if (srcSelect) {
        srcSelect.addEventListener('change', (e) => {
            const selectedSrc = e.target.value;
            let selectedTgt = tgtSelect ? tgtSelect.value : "slo";

            if (selectedSrc === selectedTgt) {
                selectedTgt = selectedSrc === "slo" ? "pl" : "slo";
                if (tgtSelect) tgtSelect.value = selectedTgt;
                safeLocalSet(STORAGE_KEYS.tgtLang, selectedTgt);
            }

            safeLocalSet(STORAGE_KEYS.srcLang, selectedSrc);
            translate();
        });
    }

    if (tgtSelect) {
        tgtSelect.addEventListener('change', (e) => {
            const selectedTgt = e.target.value;
            let selectedSrc = srcSelect ? srcSelect.value : "pl";

            if (selectedSrc === selectedTgt) {
                selectedSrc = selectedTgt === "slo" ? "pl" : "slo";
                if (srcSelect) srcSelect.value = selectedSrc;
                safeLocalSet(STORAGE_KEYS.srcLang, selectedSrc);
            }

            safeLocalSet(STORAGE_KEYS.tgtLang, selectedTgt);
            translate();
        });
    }

    await loadDictionaries();

    const userInput = document.getElementById('userInput');
    if (userInput) userInput.addEventListener('input', debounce(translate, 700));
}

function swapLanguages() {
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    if (!src || !tgt) return;

    [src.value, tgt.value] = [tgt.value, src.value];

    safeLocalSet(STORAGE_KEYS.srcLang, src.value);
    safeLocalSet(STORAGE_KEYS.tgtLang, tgt.value);

    translate();
}

function clearText() {
    const input = document.getElementById('userInput');
    const output = document.getElementById('resultOutput');

    if (input) input.value = "";
    if (output) output.innerText = "";
    hideCorrectionSuggestion();
}

function copyText() {
    const text = document.getElementById('resultOutput').innerText;
    navigator.clipboard.writeText(text);
}

async function pasteText() {
    try {
        const text = await navigator.clipboard.readText();
        const input = document.getElementById('userInput');
        if (input) {
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
        if (typeof translate === 'function') await translate();
    } catch(e) {
        console.log("Clipboard error", e);
    }
}

function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
}

window.prepareInputForTranslation = prepareInputForTranslation;
window.hideCorrectionSuggestion = hideCorrectionSuggestion;
window.googleRaw = googleRaw;
function resetInterfaceLanguageAuto() {
    safeLocalSet(STORAGE_KEYS.uiLangManual, "0");
    const lang = detectDefaultUILanguage();
    const displayLocale = getDisplayLocale(lang);
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    const currentSrc = src ? src.value : null;
    const currentTgt = tgt ? tgt.value : null;

    applyUI(lang);
    populateLanguageLists(lang, displayLocale);

    if (src && currentSrc && isSupportedLanguageCode(currentSrc)) src.value = currentSrc;
    if (tgt && currentTgt && isSupportedLanguageCode(currentTgt)) tgt.value = currentTgt;
}

window.setInterfaceLanguage = setInterfaceLanguage;
window.resetInterfaceLanguageAuto = resetInterfaceLanguageAuto;
window.onload = init;
