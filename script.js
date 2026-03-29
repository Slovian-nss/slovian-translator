let plToSlo = {}, sloToPl = {};
let wordTypes = {};

const languageData = [
    { code: 'slo', pl: 'Słowiański', en: 'Slovian (Slavic)', slo: 'Slověnьsky', de: 'Slawisch' },
    { code: 'en', pl: 'Angielski', en: 'English', slo: "Angol'ьsky", de: 'Englisch' },
    { code: 'pl', pl: 'Polski', en: 'Polish', slo: "Pol'ьsky", de: 'Polnisch' },
    { code: 'de', pl: 'Niemiecki', en: 'German', slo: 'Nemьčьsky', de: 'Deutsch' },
    { code: 'cs', pl: 'Czeski', en: 'Czech', slo: 'Češьsky', de: 'Tschechisch' },
    { code: 'sk', pl: 'Słowacki', en: 'Slovak', slo: 'Slovačьsky', de: 'Slowakisch' },
    { code: 'ru', pl: 'Rosyjski', en: 'Russian', slo: 'Rusьsky', de: 'Russisch' }
];

const uiTranslations = {
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." }
};

// --- FUNKCJA ZARZĄDZAJĄCA WIELKOŚCIĄ LITER ---
function fixCase(text, originalType) {
    if (!text) return "";
    if (originalType === "upper") return text.toUpperCase();
    if (originalType === "title") return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
    return text.toLowerCase();
}

function getCaseType(word) {
    if (word === word.toUpperCase() && word.length > 1) return "upper";
    if (word[0] === word[0].toUpperCase()) return "title";
    return "lower";
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
        if (dict[lowWord]) {
            return fixCase(dict[lowWord], getCaseType(word));
        }
        return word;
    });

    return tempText.replace(/__URL_PH_(\d+)__/g, (match, id) => placeholders[id]);
}

// --- ZMODYFIKOWANA FUNKCJA SZYKU Z KOREKTĄ WIELKOŚCI LITER ---
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

            if (wordTypes[lowToken] === "noun" && wordTypes[nextLow] === "adjective") {
                // Zachowaj informację o wielkości liter pierwszego słowa w parze
                const firstWordCase = getCaseType(token);
                
                // Przestawiamy: Przymiotnik dostaje wielkość liter Rzeczownika (jeśli był pierwszy)
                let newFirst = fixCase(nextToken, firstWordCase);
                let newSecond = fixCase(token, "lower"); // Rzeczownik ląduje w środku, więc małą literą

                result.push(newFirst);
                for (let j = i + 1; j < nextIdx; j++) result.push(tokens[j]);
                result.push(newSecond);
                i = nextIdx;
                continue;
            }
        }
        result.push(token);
    }
    return result.join("");
}

// --- RESZTA LOGIKI ---
async function translate() {
    const input = document.getElementById('userInput');
    const out = document.getElementById('resultOutput');
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;

    if (!input.value.trim()) { out.innerText = ""; return; }

    try {
        let finalResult = "";
        if (src === 'pl' && tgt === 'slo') {
            let translated = dictReplace(input.value, plToSlo);
            finalResult = reorderSmart(translated);
        } else if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(input.value, sloToPl);
        } else {
            // Logika Google Translate dla reszty
            finalResult = await google(input.value, src, tgt);
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
                        }
                    }
                });
            }
        }
        if (status) status.innerText = "Engine Ready.";
    } catch (e) { if (status) status.innerText = "Error."; }
}

function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
}

// Inicjalizacja UI (uproszczona dla czytelności)
async function init() {
    await loadDictionaries();
    document.getElementById('userInput').addEventListener('input', debounce(translate, 300));
}

window.onload = init;
