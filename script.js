// --- KONFIGURACJA I DANE ---
let plToSlo = {}, sloToPl = {};
let wordTypes = {};

const languageData = [
    { code: 'slo', slo: 'Slověnьsky', pl: 'Prasłowiański', en: 'Slovian (Proto-Slavic)', de: 'Urslawisch' },
    { code: 'pl', pl: 'Polski', en: 'Polish', slo: "Pol'ьsky", de: 'Polnisch' },
    { code: 'en', pl: 'Angielski', en: 'English', slo: "Angol'ьsky", de: 'Englisch' },
    { code: 'de', pl: 'Niemiecki', en: 'German', slo: 'Nemьčьsky', de: 'Deutsch' },
    { code: 'cs', pl: 'Czeski', en: 'Czech', slo: 'Češьsky', de: 'Tschechisch' },
    { code: 'sk', pl: 'Słowacki', en: 'Slovak', slo: 'Slovačьsky', de: 'Slowakisch' },
    { code: 'ru', pl: 'Rosyjski', en: 'Russian', slo: 'Rusьsky', de: 'Russisch' },
    { code: 'uk', pl: 'Ukraiński', en: 'Ukrainian', slo: 'Ukrajinьsky', de: 'Ukrainisch' },
    { code: 'be', pl: 'Białoruski', en: 'Belarusian', slo: 'Bělorusьsky', de: 'Weißrussisch' },
    { code: 'bg', pl: 'Bułgarski', en: 'Bulgarian', slo: "Boulgar'ьsky", de: 'Bulgarisch' },
    { code: 'hr', pl: 'Chorwacki', en: 'Croatian', slo: 'Horvatьsky', de: 'Kroatisch' },
    { code: 'sr', pl: 'Serbski (cyrylica)', en: 'Serbian (Cyrillic)', slo: 'Sirbьsky (kyrilica)', de: 'Serbisch (Kyrillisch)' },
    { code: 'sr-Latn', pl: 'Serbski (łacina)', en: 'Serbian (Latin)', slo: 'Sirbьsky (latinica)', de: 'Serbisch (Latein)' },
    { code: 'sl', pl: 'Słoweński', en: 'Slovenian', slo: 'Slovenečьsky', de: 'Slowenisch' },
    { code: 'mk', pl: 'Macedoński', en: 'Macedonian', slo: 'Makedonьsky', de: 'Mazedonisch' },
    { code: 'fr', pl: 'Francuski', en: 'French', slo: 'Franьsky', de: 'Französisch' },
    { code: 'es', pl: 'Hiszpański', en: 'Spanish', slo: 'Španьsky', de: 'Spanisch' },
    { code: 'it', pl: 'Włoski', en: 'Italian', slo: 'Volšьsky', de: 'Italienisch' },
    { code: 'pt', pl: 'Portugalski', en: 'Portuguese', slo: "Portugal'ьsky", de: 'Portugiesisch' },
    { code: 'nl', pl: 'Holenderski', en: 'Dutch', slo: 'Niskozemьsky', de: 'Niederländisch' },
    { code: 'da', pl: 'Duński', en: 'Danish', slo: 'Dunьsky', de: 'Dänisch' },
    { code: 'sv', pl: 'Szwedzki', en: 'Swedish', slo: 'Švedьsky', de: 'Schwedisch' },
    { code: 'no', pl: 'Norweski', en: 'Norwegian', slo: 'Norvežьsky', de: 'Norwegisch' },
    { code: 'fi', pl: 'Fiński', en: 'Finnish', slo: 'Finьsky', de: 'Finnisch' },
    { code: 'et', pl: 'Estoński', en: 'Estonian', slo: 'Estonьsky', de: 'Estnisch' },
    { code: 'lv', pl: 'Łotewski', en: 'Latvian', slo: 'Latyšьsky', de: 'Lettisch' },
    { code: 'lt', pl: 'Litewski', en: 'Lithuanian', slo: 'Litovьsky', de: 'Litauisch' },
    { code: 'el', pl: 'Grecki', en: 'Greek', slo: 'Grečьsky', de: 'Griechisch' },
    { code: 'tr', pl: 'Turecki', en: 'Turkish', slo: 'Turečьsky', de: 'Türkisch' },
    { code: 'hu', pl: 'Węgierski', en: 'Hungarian', slo: 'Ǫgrinьsky', de: 'Ungarisch' },
    { code: 'ro', pl: 'Rumuński', en: 'Romanian', slo: "Rumunьsky", de: 'Rumänisch' },
    { code: 'ja', pl: 'Japoński', en: 'Japanese', slo: 'Japonьsky', de: 'Japanisch' },
    { code: 'ko', pl: 'Koreański', en: 'Korean', slo: 'Koreanьsky', de: 'Koreanisch' },
    { code: 'zh-CN', pl: 'Chiński (upr.)', en: 'Chinese (Simp.)', slo: 'Kitajьsky (uprošč.)', de: 'Chinesisch' },
    { code: 'ar', pl: 'Arabski', en: 'Arabic', slo: 'Arabьsky', de: 'Arabisch' },
    { code: 'hi', pl: 'Hindi', en: 'Hindi', slo: 'Hindьsky', de: 'Hindi' },
    { code: 'id', pl: 'Indonezyjski', en: 'Indonesian', slo: 'Indonezijьsky', de: 'Indonesisch' },
    { code: 'vi', pl: 'Wietnamski', en: 'Vietnamese', slo: 'Větnamьsky', de: 'Vietnamesisch' }
];

const uiTranslations = {
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." },
    de: { title: "Slovo Übersetzer", from: "Von:", to: "Nach:", paste: "Einfügen", clear: "Löschen", copy: "Kopieren", placeholder: "Text eingeben..." }
};

// --- FUNKCJE INTERFEJSU ---
function populateLanguageLists(uiLang, userLocale) {
    const s1 = document.getElementById('srcLang'), s2 = document.getElementById('tgtLang');
    if (!s1 || !s2) return;
    let dn;
    try { dn = new Intl.DisplayNames([userLocale], { type: 'language' }); } catch (e) {}

    [s1, s2].forEach(s => {
        s.options.length = 0;
        languageData.forEach(l => {
            let name = "";
            if (l.code === 'slo') {
                name = l[uiLang] || l.en || l.slo;
            } else {
                try {
                    name = dn ? dn.of(l.code) : (l[uiLang] || l.en);
                } catch (e) { name = l[uiLang] || l.en; }
            }
            // Specyficzna poprawka dla serbskiego w liście wyboru
            if (l.code === 'sr') name = (uiLang === 'pl') ? "Serbski (cyrylica)" : "Serbian (Cyrillic)";
            if (l.code === 'sr-Latn') name = (uiLang === 'pl') ? "Serbski (łacina)" : "Serbian (Latin)";

            name = name.charAt(0).toUpperCase() + name.slice(1);
            s.add(new Option(name, l.code));
        });
    });
}

function applyUI(lang) {
    const ui = uiTranslations[lang] || uiTranslations.en;
    const elements = {
        'ui-title': ui.title,
        'ui-label-from': ui.from,
        'ui-label-to': ui.to,
        'ui-paste': ui.paste,
        'ui-clear': ui.clear,
        'ui-copy': ui.copy
    };
    Object.keys(elements).forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = elements[id];
    });
    const input = document.getElementById('userInput');
    if (input) input.placeholder = ui.placeholder;
}

// --- FUNKCJE WIELKOŚCI LITER (CASE MAPPING) ---
function getCase(word) {
    if (!word) return "lower";
    if (word === word.toUpperCase() && word.length > 1) return "upper";
    if (word[0] === word[0].toUpperCase()) return "title";
    return "lower";
}

function applyCase(word, caseType) {
    if (!word) return "";
    if (caseType === "upper") return word.toUpperCase();
    if (caseType === "title") return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    return word.toLowerCase();
}

// --- LOGIKA TŁUMACZENIA I SZYKU ---
function dictReplace(text, dict) {
    if (!text) return "";
    const urlRegex = /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
    let placeholders = [];
    let tempText = text.replace(urlRegex, (match) => {
        placeholders.push(match);
        return `__URL_PH_${placeholders.length - 1}__`;
    });

    // Rozpoznawanie słów uwzględniające znaki prasłowiańskie
    tempText = tempText.replace(/[a-ząćęłńóśźżěьъǫę']+/gi, (word) => {
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

        if (wordTypes[lowToken]) {
            let group = [];
            let currentIdx = i;
            let firstWordCase = getCase(tokens[i]);

            while (currentIdx < tokens.length) {
                let currentToken = tokens[currentIdx];
                if (/^[\s]+$/.test(currentToken)) { currentIdx++; continue; }
                
                let currentLow = currentToken.toLowerCase();
                let type = wordTypes[currentLow];
                if (type === "noun" || type === "adjective" || type === "numeral") {
                    group.push({ val: currentToken, type: type });
                    i = currentIdx;
                    currentIdx++;
                } else { break; }
            }

            if (group.length > 1) {
                const order = { "numeral": 1, "adjective": 2, "noun": 3 };
                group.sort((a, b) => (order[a.type] || 99) - (order[b.type] || 99));

                group.forEach((word, index) => {
                    let formattedWord = (index === 0) ? applyCase(word.val, firstWordCase) : 
                                        (firstWordCase === "upper" ? word.val.toUpperCase() : word.val.toLowerCase());
                    result.push(formattedWord);
                    if (index < group.length - 1) result.push(" ");
                });
                continue;
            }
        }
        result.push(token);
    }
    return result.join("");
}

// --- KOMUNIKACJA Z API (Z BRIDGE TRANSLATION) ---
async function google(text, s, t) {
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data[0].map(x => x[0]).join('');
    } catch (e) { return text; }
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

        // SCENARIUSZ: Słowiański -> Inny (przez Polski)
        if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            finalResult = (tgt === 'pl') ? bridge : await google(bridge, 'pl', tgt);
        } 
        // SCENARIUSZ: Inny -> Słowiański (przez Polski)
        else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            let translated = dictReplace(bridge, plToSlo);
            finalResult = reorderSmart(translated);
        } 
        // SCENARIUSZ: Standardowe tłumaczenie między językami Google
        else {
            finalResult = await google(text, src, tgt);
        }

        out.innerText = finalResult;
    } catch (e) { 
        console.error(e);
        out.innerText = "Error..."; 
    }
}

// --- ZASOBY I INICJALIZACJA ---
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
    const sysLocale = navigator.language || 'en';
    const sysLang = sysLocale.split('-')[0];
    const uiKey = uiTranslations[sysLang] ? sysLang : 'en';

    applyUI(uiKey);
    populateLanguageLists(uiKey, sysLocale);

    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');

    srcSelect.value = localStorage.getItem('srcLang') || 'pl';
    tgtSelect.value = localStorage.getItem('tgtLang') || 'slo';

    [srcSelect, tgtSelect].forEach(s => {
        s.addEventListener('change', () => {
            localStorage.setItem('srcLang', srcSelect.value);
            localStorage.setItem('tgtLang', tgtSelect.value);
            translate();
        });
    });

    await loadDictionaries();
    const userInput = document.getElementById('userInput');
    if (userInput) userInput.addEventListener('input', debounce(translate, 300));
}

// --- AKCJE PRZYCISKÓW ---
function swapLanguages() {
    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');
    const input = document.getElementById('userInput');
    const output = document.getElementById('resultOutput');

    // Zamiana języków
    const tempLang = srcSelect.value;
    srcSelect.value = tgtSelect.value;
    tgtSelect.value = tempLang;

    localStorage.setItem('srcLang', srcSelect.value);
    localStorage.setItem('tgtLang', tgtSelect.value);

    // Przerzucenie tekstu (odwrócenie tłumaczenia)
    if (output.innerText.trim() !== "") {
        input.value = output.innerText;
    }
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
