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

const uiTranslations = { /* ... Twój obszerny obiekt UI bez zmian ... */ };

// ---------------- WIELKOŚĆ LITER ----------------
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

// ---------------- REPLACE SŁOWNIKOWY ----------------
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
        return "__MISSING__"; // brak w słowniku
    });
    return tempText.replace(/__URL_PH_(\d+)__/g, (match, id) => placeholders[id]);
}

// ---------------- REORDER SMART ----------------
function reorderSmart(text) {
    if (!text) return "";
    const tokens = text.split(/(\s+|[.,!?;:()=+\-%*/]+)/g).filter(t => t !== "" && t !== undefined);
    const result = [];
    for (let i = 0; i < tokens.length; i++) {
        let token = tokens[i];
        let lowToken = token.toLowerCase();
        if (/^[\s.,!?;:()=+\-%*/]+$/.test(token)) {
            result.push(token); continue;
        }
        if (wordTypes[lowToken]) {
            let group = [];
            let currentIdx = i;
            let firstWordCase = getCase(tokens[i]);
            while (currentIdx < tokens.length) {
                let currentToken = tokens[currentIdx];
                let currentLow = currentToken.toLowerCase();
                if (/^[\s]+$/.test(currentToken)) { currentIdx++; continue; }
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
                    let formattedWord = word.val.toLowerCase();
                    if (index === 0) formattedWord = applyCase(word.val, firstWordCase);
                    else if (firstWordCase === "upper") formattedWord = word.val.toUpperCase();
                    result.push(formattedWord);
                    if (index < group.length - 1) result.push(" ");
                });
                continue;
            } else if (group.length === 1) { result.push(token); continue; }
        }
        result.push(token);
    }
    return result.join("");
}

// ---------------- FUNKCJA HYBRYDOWA ----------------
async function hybridTranslate(text, src, tgt) {
    let translated = dictReplace(text, src === 'pl' ? plToSlo : sloToPl);
    if (translated.includes("__MISSING__")) {
        try {
            const res = await fetch("http://localhost:11434/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    model: "qwen",
                    prompt: `Translate to Slovian preserving cases: ${text}`
                })
            });
            const data = await res.json();
            translated = data.response;
        } catch(e) { console.log("Hybrid translate API failed", e); }
    }
    return reorderSmart(translated);
}

// ---------------- FUNKCJA TŁUMACZENIA ----------------
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
        if (src === 'pl' && tgt === 'slo') {
            finalResult = await hybridTranslate(text, src, tgt);
        } else if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(text, sloToPl);
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

// ---------------- GOOGLE TRANSLATE ----------------
async function google(text, s, t) {
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data[0].map(x => x[0]).join('');
    } catch (e) { return text; }
}

// ---------------- ŁADOWANIE SŁOWNIKÓW ----------------
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

// ---------------- INIT ----------------
async function init() {
    const sysLocale = navigator
