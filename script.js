let plToSlo = {}, sloToPl = {};
let wordTypes = {};

const languageData = [
    { code: 'slo', pl: 'Słowiański', en: 'Slovian (Slavic)', slo: 'Slověnьsky', de: 'Slawisch' },
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
    es: { title: "Traductor Slovo", from: "De:", to: "A:", paste: "Pegar", clear: "Borrar", copy: "Copiar", placeholder: "Escribe texto..." },
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
    sr: { title: "Slovo Преводилац", from: "Са:", to: "На:", paste: "Налепи", clear: "Обриши", copy: "Копирај", placeholder: "Унеси текст..." },
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

// Zachowuje wielkość liter (Case Sensitive)
function preserveCase(original, translated) {
    if (!translated) return original;
    if (original === original.toUpperCase() && original.length > 1) return translated.toUpperCase();
    if (original[0] === original[0].toUpperCase()) return translated.charAt(0).toUpperCase() + translated.slice(1);
    return translated.toLowerCase();
}

// Tłumaczy słowa, ignorując linki, liczby i interpunkcję
function dictReplace(text, dict) {
    if (!text) return "";
    // Wykrywa słowa (w tym z apostrofem i znakami słowiańskimi), omija linki i e-maile
    const urlRegex = /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
    
    // Najpierw zabezpieczamy linki
    let placeholders = [];
    let tempText = text.replace(urlRegex, (match) => {
        placeholders.push(match);
        return `__URL_PH_${placeholders.length - 1}__`;
    });

    // Tłumaczymy słowa
    tempText = tempText.replace(/[a-ząćęłńóśźżěьъ']+/gi, (word) => {
        const lowWord = word.toLowerCase();
        if (dict[lowWord]) {
            return preserveCase(word, dict[lowWord]);
        }
        return word;
    });

    // Przywracamy linki
    return tempText.replace(/__URL_PH_(\d+)__/g, (match, id) => placeholders[id]);
}

// Zamienia szyk: jeśli Rzeczownik + Przymiotnik -> Przymiotnik + Rzeczownik
function reorderSmart(text) {
    if (!text) return "";
    // Dzieli na słowa, spacje i znaki interpunkcyjne
    const tokens = text.split(/(\s+|[.,!?;:()=+\-%*/]+)/g).filter(t => t !== "" && t !== undefined);
    const result = [];

    for (let i = 0; i < tokens.length; i++) {
        let token = tokens[i];
        let lowToken = token.toLowerCase();

        // Jeśli to spacja lub interpunkcja, dodaj i leć dalej
        if (/^[\s.,!?;:()=+\-%*/]+$/.test(token)) {
            result.push(token);
            continue;
        }

        let nextIdx = i + 1;
        // Szukaj następnego słowa (pomiń tylko spacje)
        while (nextIdx < tokens.length && /^[\s]+$/.test(tokens[nextIdx])) nextIdx++;

        if (nextIdx < tokens.length) {
            let nextToken = tokens[nextIdx];
            let nextLow = nextToken.toLowerCase();

            // LOGIKA ZAMIANY (Rzeczownik + Przymiotnik -> Przymiotnik + Rzeczownik)
            if (wordTypes[lowToken] === "noun" && wordTypes[nextLow] === "adjective") {
                result.push(nextToken); // Przymiotnik najpierw
                for (let j = i + 1; j < nextIdx; j++) result.push(tokens[j]); // Spacje pomiędzy
                result.push(token); // Rzeczownik potem
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
                            // Dopasowanie do Twojego formatu: jimenьnik (noun), priloga (adj), ličьnik (num)
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
