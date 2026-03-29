let plToSlo = {}, sloToPl = {};
let dictionaryData = []; // Globalna baza do sprawdzania typów części mowy

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
    ru: { title: "Slovo Переводчик", from: "С языка:", to: "На язык:", paste: "Вставить", clear: "Очистить", copy: "Копировать", placeholder: "Введите текст..." },
    // Dodaj resztę według potrzeb...
};

// Pomocnicza funkcja do sprawdzania typu słowa w bazie danych
function findType(word) {
    const cleanWord = word.toLowerCase().replace(/[.!?,\s]/g, '');
    const entry = dictionaryData.find(d => d.slovian && d.slovian.toLowerCase() === cleanWord);
    if (entry && entry['type and case']) {
        const t = entry['type and case'].toLowerCase();
        if (t.includes('numeral')) return 1;
        if (t.includes('adjective')) return 2;
        if (t.includes('noun')) return 3;
    }
    return 99; // nieznane
}

function dictReplace(text, dict) {
    return text.replace(/[a-ząćęłńóśźżěьъǫ\u0300-\u036f'‘’]+/gi, (m) => {
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

function smartReorder(slovianText) {
    // Dzieli tekst na segmenty (zdania/frazy po przecinkach), aby nie mieszać słów między zdaniami
    return slovianText.split(/([.!?\n,]+)/).map(segment => {
        if (/^[.!?\n,]+$/.test(segment) || !segment.trim()) return segment;

        const tokens = segment.split(/(\s+)/);
        let wordsInOrder = [];

        // Wyłuskujemy słowa i sprawdzamy ich wagi
        tokens.forEach((token, index) => {
            if (/[a-ząćęłńóśźżěьъǫ\u0300-\u036f]+/i.test(token)) {
                wordsInOrder.push({
                    text: token,
                    weight: findType(token)
                });
            }
        });

        if (wordsInOrder.length < 2) return segment;

        // Sortowanie: Liczebnik (1) -> Przymiotnik (2) -> Rzeczownik (3)
        wordsInOrder.sort((a, b) => a.weight - b.weight);

        // Składanie z powrotem
        let wordIdx = 0;
        return tokens.map(token => {
            if (/[a-ząćęłńóśźżěьъǫ\u0300-\u036f]+/i.test(token)) {
                return wordsInOrder[wordIdx++].text;
            }
            return token;
        }).join('');
    }).join('');
}

async function translate() {
    const text = document.getElementById('userInput').value.trim();
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;
    const out = document.getElementById('resultOutput');
    
    if (!text) { out.innerText = ""; return; }
    
    try {
        let finalResult = "";
        if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(text, sloToPl);
        } else if (src === 'pl' && tgt === 'slo') {
            let temp = dictReplace(text, plToSlo);
            finalResult = smartReorder(temp);
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            finalResult = await google(bridge, 'pl', tgt);
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            let temp = dictReplace(bridge, plToSlo);
            finalResult = smartReorder(temp);
        } else {
            finalResult = await google(text, src, tgt);
        }
        out.innerText = finalResult || "";
    } catch (e) { out.innerText = "Translation error..."; }
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
                dictionaryData = [...dictionaryData, ...data]; // Zachowujemy pełne obiekty do sprawdzania typów
                data.forEach(item => {
                    if (item.polish && item.slovian) {
                        plToSlo[item.polish.toLowerCase().trim()] = item.slovian.trim();
                        sloToPl[item.slovian.toLowerCase().trim()] = item.polish.trim();
                    }
                });
            }
        }
        if(status) status.innerText = "Engine Ready.";
    } catch (e) { if(status) status.innerText = "Dict Error."; }
}

async function init() {
    const sysLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[sysLang] ? sysLang : 'en';
    applyUI(uiKey);
    populateLanguageLists(uiKey);
    
    let defaultSrc = 'en';
    let defaultTgt = 'slo';
    if (sysLang === 'pl') defaultSrc = 'pl';
    
    document.getElementById('srcLang').value = localStorage.getItem('srcLang') || defaultSrc;
    document.getElementById('tgtLang').value = localStorage.getItem('tgtLang') || defaultTgt;
    
    await loadDictionaries();
    
    document.getElementById('userInput').addEventListener('input', debounce(() => translate(), 300));
    document.getElementById('srcLang').onchange = (e) => { localStorage.setItem('srcLang', e.target.value); translate(); };
    document.getElementById('tgtLang').onchange = (e) => { localStorage.setItem('tgtLang', e.target.value); translate(); };
}

function applyUI(lang) {
    const ui = uiTranslations[lang] || uiTranslations.en;
    const elements = ['ui-title', 'ui-label-from', 'ui-label-to', 'ui-paste', 'ui-clear', 'ui-copy'];
    elements.forEach(id => {
        const el = document.getElementById(id);
        if(el) {
            const key = id.replace('ui-', '');
            el.innerText = ui[key];
        }
    });
    if(document.getElementById('userInput')) document.getElementById('userInput').placeholder = ui.placeholder;
}

function populateLanguageLists(uiLang) {
    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');
    if(!srcSelect || !tgtSelect) return;
    srcSelect.options.length = 0;
    tgtSelect.options.length = 0;
    languageData.forEach(lang => {
        const name = lang[uiLang] || lang.en;
        srcSelect.add(new Option(name, lang.code));
        tgtSelect.add(new Option(name, lang.code));
    });
}

function swapLanguages() {
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    const temp = src.value;
    src.value = tgt.value;
    tgt.value = temp;
    localStorage.setItem('srcLang', src.value);
    localStorage.setItem('tgtLang', tgt.value);
    translate();
}

async function pasteText() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById('userInput').value = text;
        translate();
    } catch(e) { alert("Please allow clipboard access"); }
}

function copyText() {
    const text = document.getElementById('resultOutput').innerText;
    navigator.clipboard.writeText(text);
}

function clearText() {
    document.getElementById('userInput').value = "";
    document.getElementById('resultOutput').innerText = "";
}

function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
}

window.onload = init;
