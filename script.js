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
    { code: 'uk', pl: 'Ukraiński', en: 'Ukrainian', slo: 'Ukrajinьsky', de: 'Ukrainisch' }
    // Możesz dodać resztę języków tutaj...
];

const uiTranslations = {
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." }
};

// Funkcja dopasowująca wielkość liter (Case Sensitivity)
function matchCase(original, target) {
    if (original === original.toUpperCase()) return target.toUpperCase();
    if (original[0] === original[0].toUpperCase()) return target.charAt(0).toUpperCase() + target.slice(1).toLowerCase();
    return target.toLowerCase();
}

// Funkcja naprawiająca szyk: Rzeczownik + Przymiotnik -> Przymiotnik + Rzeczownik
function fixSlovianWordOrder(text) {
    // Rozbijamy na słowa, spacje i interpunkcję
    let tokens = text.split(/([a-ząćęłńóśźżěьъ]+|\s+|[.,!?;:]+)/gi).filter(Boolean);
    
    for (let i = 0; i < tokens.length - 2; i++) {
        let current = tokens[i];
        let next = tokens[i + 2];
        
        if (!next) continue;

        let cleanA = current.toLowerCase().replace(/[.,!?;:]/g, "").trim();
        let cleanB = next.toLowerCase().replace(/[.,!?;:]/g, "").trim();

        if (wordTypes[cleanA] === 'noun' && (wordTypes[cleanB] === 'adjective' || wordTypes[cleanB] === 'numeral')) {
            let punctA = current.match(/[.,!?;:]+$/) || "";
            let punctB = next.match(/[.,!?;:]+$/) || "";

            // Zamiana
            let newFirst = matchCase(current, cleanB);
            let newSecond = matchCase(next, cleanA);

            tokens[i] = newFirst; 
            tokens[i + 2] = newSecond + punctB + punctA; // Przenosimy interpunkcję na koniec
            i += 2;
        }
    }
    return tokens.join('');
}

function dictReplace(text, dict) {
    return text.replace(/[a-ząćęłńóśźżěьъ]+/gi, (m) => {
        const low = m.toLowerCase();
        if (dict[low]) {
            const r = dict[low];
            if (m === m.toUpperCase()) return r.toUpperCase();
            if (m[0] === m[0].toUpperCase()) return r.charAt(0).toUpperCase() + r.slice(1);
            return r;
        }
        return m;
    });
}

async function google(text, s, t) {
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data[0].map(x => x[0]).join('');
    } catch (e) { return text; }
}

async function translate() {
    const text = document.getElementById('userInput').value.trim();
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;
    const out = document.getElementById('resultOutput');
    
    if (!text) { out.innerText = ""; return; }
    
    try {
        let res = "";
        if (src === 'pl' && tgt === 'slo') {
            res = fixSlovianWordOrder(dictReplace(text, plToSlo));
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            res = fixSlovianWordOrder(dictReplace(bridge, plToSlo));
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            res = await google(bridge, 'pl', tgt);
        } else {
            res = await google(text, src, tgt);
        }
        out.innerText = res;
    } catch (e) { out.innerText = "..."; }
}

async function loadDictionaries() {
    try {
        const files = ['osnova.json', 'vuzor.json'];
        for (const file of files) {
            const res = await fetch(file);
            if (res.ok) {
                const data = await res.json();
                data.forEach(item => {
                    if (item.polish && item.slovian) {
                        let s = item.slovian.toLowerCase().trim();
                        let p = item.polish.toLowerCase().trim();
                        plToSlo[p] = item.slovian.trim();
                        sloToPl[s] = item.polish.trim();
                        
                        let info = (item['type and case'] || "").toLowerCase();
                        if (info.includes('noun') || info.includes('jimenovnik')) wordTypes[s] = 'noun';
                        else if (info.includes('adjective') || info.includes('pridavnik')) wordTypes[s] = 'adjective';
                        else if (info.includes('numeral') || info.includes('ličebnik')) wordTypes[s] = 'numeral';
                    }
                });
            }
        }
        document.getElementById('dbStatus').innerText = "Engine Ready.";
    } catch (e) { document.getElementById('dbStatus').innerText = "Load Error."; }
}

function applyUI(langKey) {
    const ui = uiTranslations[langKey] || uiTranslations.en;
    document.getElementById('ui-title').innerText = ui.title;
    document.getElementById('ui-label-from').innerText = ui.from;
    document.getElementById('ui-label-to').innerText = ui.to;
    document.getElementById('ui-paste').innerText = ui.paste;
    document.getElementById('ui-clear').innerText = ui.clear;
    document.getElementById('ui-copy').innerText = ui.copy;
    document.getElementById('userInput').placeholder = ui.placeholder;
}

function populateLanguageLists(uiLang) {
    const srcS = document.getElementById('srcLang');
    const tgtS = document.getElementById('tgtLang');
    srcS.innerHTML = ""; tgtS.innerHTML = "";
    languageData.forEach(l => {
        const name = l[uiLang] || l.en;
        srcS.add(new Option(name, l.code));
        tgtS.add(new Option(name, l.code));
    });
}

// Funkcje przycisków
function clearText() {
    document.getElementById('userInput').value = "";
    document.getElementById('resultOutput').innerText = "";
}

async function pasteText() {
    const text = await navigator.clipboard.readText();
    document.getElementById('userInput').value = text;
    translate();
}

function copyText() {
    navigator.clipboard.writeText(document.getElementById('resultOutput').innerText);
}

const debounce = (fn, ms) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(null, args), ms);
    };
};

async function init() {
    // Wykrywanie języka urządzenia
    const browserLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[browserLang] ? browserLang : 'en';
    
    applyUI(uiKey);
    populateLanguageLists(uiKey);

    // Ustawienie domyślnych języków
    document.getElementById('srcLang').value = localStorage.getItem('srcLang') || (browserLang === 'pl' ? 'pl' : 'en');
    document.getElementById('tgtLang').value = localStorage.getItem('tgtLang') || 'slo';

    await loadDictionaries();

    // Event Listeners
    document.getElementById('userInput').addEventListener('input', debounce(translate, 300));
    document.getElementById('srcLang').onchange = (e) => { localStorage.setItem('srcLang', e.target.value); translate(); };
    document.getElementById('tgtLang').onchange = (e) => { localStorage.setItem('tgtLang', e.target.value); translate(); };
    
    // Podpięcie przycisków (ważne!)
    document.getElementById('ui-clear').onclick = clearText;
    document.getElementById('ui-paste').onclick = pasteText;
    document.getElementById('ui-copy').onclick = copyText;
}

window.onload = init;
