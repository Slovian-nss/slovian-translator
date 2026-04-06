// declination.js
// Moduł do tworzenia fleksji/deklinacji słów w starosłowiańskim (PL→SLO lub dowolny język)
// Autor: Ernest Pruszyński
// Możesz go importować w swoim projekcie np. import { flexWord, getWordCases } from './declination.js'

const wordCases = {}; // przechowuje wszystkie odmiany słów

/**
 * Pobiera typ liter w słowie (małe, wielkie, tytuł)
 * @param {string} word
 * @returns {string} - "lower", "upper", "title"
 */
function getCase(word){
    if(!word) return "lower";
    if(word === word.toUpperCase() && word.length>1) return "upper";
    if(word[0]===word[0].toUpperCase()) return "title";
    return "lower";
}

/**
 * Zastosowanie typu liter do słowa
 * @param {string} word
 * @param {string} caseType
 * @returns {string}
 */
function applyCase(word, caseType){
    if(!word) return "";
    switch(caseType){
        case "upper": return word.toUpperCase();
        case "title": return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        default: return word.toLowerCase();
    }
}

/**
 * Tworzy deklinacje (7 przypadków) dla pojedynczego słowa
 * @param {string} word
 * @returns {object} - {nom: "", gen: "", dat: "", acc: "", inst: "", loc: "", voc: ""}
 */
function flexWord(word){
    const lower = word.toLowerCase();
    if(wordCases[lower]) return wordCases[lower]; // jeśli już mamy, zwracamy
    
    // Typ liter słowa (zachowanie wielkości)
    const caseType = getCase(word);

    // 7 przypadków starosłowiańskich (placeholder)
    const cases = ["nom", "gen", "dat", "acc", "inst", "loc", "voc"];
    let flex = {};

    cases.forEach(c => {
        // na razie prosty placeholder: można tu wprowadzić reguły odmiany
        flex[c] = applyCase(word, caseType);
    });

    wordCases[lower] = flex;
    return flex;
}

/**
 * Pobiera wszystkie zapisane deklinacje słów
 * @returns {object} wordCases
 */
function getWordCases(){
    return wordCases;
}

/**
 * Funkcja pomocnicza: drukuje fleksję w konsoli
 * @param {string} word
 */
function printFlex(word){
    const flex = flexWord(word);
    console.log(`Fleksja dla "${word}":`);
    Object.keys(flex).forEach(c => console.log(`${c}: ${flex[c]}`));
}

// Eksport modułu
export { flexWord, getWordCases, printFlex };
