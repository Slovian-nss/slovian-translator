/* slovo_declension_patch.js
 * Bezpieczna warstwa odmiany przez wzory z vuzor.json.
 * Naprawia: interpunkcję, placeholder 🔴 oraz nieznane rzeczowniki typu mydło -> mydlo
 * przez dobór najbliższego wzoru, np. kadzidło -> kadidlo.
 */
(function () {
  "use strict";

  const IDS = { input: "userInput", output: "resultOutput", src: "srcLang", tgt: "tgtLang", sugg: "suggestionBox" };

  const CASES = ["nominative", "accusative", "genitive", "locative", "dative", "instrumental", "vocative"];
  const NUMBERS = ["singular", "plural"];

  const PREP_CASE = new Map([
    ["do", "genitive"], ["od", "genitive"], ["bez", "genitive"], ["dla", "genitive"], ["u", "genitive"], ["około", "genitive"], ["wokół", "genitive"],
    ["ku", "dative"], ["dzięki", "dative"], ["wbrew", "dative"], ["przeciw", "dative"], ["przeciwko", "dative"],
    ["w", "locative"], ["we", "locative"], ["na", "locative"], ["po", "locative"], ["przy", "locative"], ["o", "locative"],
    ["z", "instrumental"], ["ze", "instrumental"], ["nad", "instrumental"], ["pod", "instrumental"], ["przed", "instrumental"], ["między", "instrumental"], ["pomiędzy", "instrumental"], ["za", "instrumental"]
  ]);

  const PREP_SLO = new Map([
    ["w", "vu"], ["we", "vu"], ["na", "na"], ["po", "po"], ["przy", "pri"], ["o", "ob"],
    ["z", "su"], ["ze", "su"], ["do", "do"], ["od", "ot"], ["bez", "bez"], ["dla", "dlja"], ["u", "u"],
    ["nad", "nad"], ["pod", "pod"], ["przed", "pred"], ["między", "medju"], ["pomiędzy", "medju"], ["za", "za"],
    ["ku", "ku"], ["dzięki", "blagodarja"], ["wbrew", "vupreki"], ["przeciw", "protivu"], ["przeciwko", "protivu"]
  ]);

  const STATE = {
    loaded: false,
    loading: null,
    patterns: [],
    exact: new Map(),
    lemmas: new Map()
  };

  let timer = null;

  function $(id) { return document.getElementById(id); }

  function normalize(value) {
    return String(value || "").normalize("NFC").replace(/[’]/g, "'").replace(/\s+/g, " ").trim().toLocaleLowerCase("pl");
  }

  function foldPl(value) {
    return normalize(value).replace(/[ąćęłńóśźż]/g, ch => ({ ą: "a", ć: "c", ę: "e", ł: "l", ń: "n", ó: "o", ś: "s", ź: "z", ż: "z" })[ch] || ch);
  }

  function foldSlo(value) {
    return normalize(value).replace(/[ěęǫьъšžčćńłóśźż]/g, ch => ({ ě: "e", ę: "e", ǫ: "o", ь: "", ъ: "", š: "s", ž: "z", č: "c", ć: "c", ń: "n", ł: "l", ó: "o", ś: "s", ź: "z", ż: "z" })[ch] || ch);
  }

  function parseMeta(typeCase) {
    const raw = String(typeCase || "");
    const x = normalize(raw);
    const m = { noun: false, c: null, n: null, g: null, a: null };

    m.noun = x.includes("noun") || x.includes("jimenьnik") || x.includes("imenьnik") || x.includes("rzeczownik") || x.includes("jimenitelj") || x.includes("vinitelj") || x.includes("roditelj") || x.includes("městьnik") || x.includes("tvoritelj") || x.includes("zovatelj");
    if (x.includes("adjective") || x.includes("pridav") || x.includes("przymiotnik")) m.noun = false;

    if (x.includes("nominative") || x.includes("jimenovьnik") || x.includes("jimenitelj")) m.c = "nominative";
    else if (x.includes("accusative") || x.includes("vinьnik") || x.includes("vinitelj")) m.c = "accusative";
    else if (x.includes("genitive") || x.includes("rodilьnik") || x.includes("roditelj")) m.c = "genitive";
    else if (x.includes("locative") || x.includes("městьnik")) m.c = "locative";
    else if (x.includes("dative") || x.includes("měrьnik")) m.c = "dative";
    else if (x.includes("instrumental") || x.includes("orǫdьnik") || x.includes("tvoritelj")) m.c = "instrumental";
    else if (x.includes("vocative") || x.includes("zovanьnik") || x.includes("zovatelj")) m.c = "vocative";

    if (x.includes("singular") || x.includes("poedinьna")) m.n = "singular";
    else if (x.includes("plural") || x.includes("munoga") || x.includes("munga")) m.n = "plural";

    if (x.includes("feminine") || x.includes("žen") || x.includes("żeński") || x.includes("zenski")) m.g = "feminine";
    else if (x.includes("neuter") || x.includes("nijak")) m.g = "neuter";
    else if (x.includes("masculine") || x.includes("mǫž") || x.includes("męski") || x.includes("meski")) m.g = "masculine";

    if (x.includes("inanimate") || x.includes("neživot") || x.includes("nieżywot") || x.includes("niezywot")) m.a = "inanimate";
    else if (x.includes("animate") || x.includes("život") || x.includes("żywot") || x.includes("zywot")) m.a = "animate";

    return m;
  }

  function slot(c, n) { return `${c}|${n}`; }

  function commonPrefix(a, b) {
    const aa = Array.from(String(a || ""));
    const bb = Array.from(String(b || ""));
    let i = 0;
    while (i < aa.length && i < bb.length && aa[i] === bb[i]) i++;
    return i;
  }

  function commonSuffix(a, b, fold) {
    const aa = Array.from(fold(a));
    const bb = Array.from(fold(b));
    let i = 0;
    while (i < aa.length && i < bb.length && aa[aa.length - 1 - i] === bb[bb.length - 1 - i]) i++;
    return i;
  }

  function makeTransform(base, form) {
    const p = commonPrefix(base, form);
    return { remove: Array.from(base).length - p, append: Array.from(form).slice(p).join("") };
  }

  function applyTransform(base, tr) {
    const arr = Array.from(String(base || ""));
    const keep = Math.max(0, arr.length - (tr.remove || 0));
    return arr.slice(0, keep).join("") + String(tr.append || "");
  }

  function inferGender(slovian, fallback) {
    if (fallback) return fallback;
    const w = normalize(slovian);
    if (w.endsWith("ostь") || w.endsWith("ь") || w.endsWith("a") || w.endsWith("ja")) return "feminine";
    if (w.endsWith("o") || w.endsWith("e") || w.endsWith("ę") || w.endsWith("je") || w.endsWith("ьje") || w.endsWith("stvo")) return "neuter";
    return "masculine";
  }

  function plClass(w) {
    const x = foldPl(w);
    if (x.endsWith("dlo")) return "dlo";
    if (x.endsWith("lo")) return "lo";
    if (x.endsWith("osc")) return "osc";
    if (x.endsWith("stwo")) return "stwo";
    if (x.endsWith("anie") || x.endsWith("enie")) return "nie";
    if (x.endsWith("od")) return "od";
    if (x.endsWith("or")) return "or";
    if (x.endsWith("a")) return "a";
    if (x.endsWith("o")) return "o";
    if (x.endsWith("e")) return "e";
    return "cons";
  }

  function sloClass(w) {
    const x = normalize(w);
    if (x.endsWith("dlo")) return "dlo";
    if (x.endsWith("lo")) return "lo";
    if (x.endsWith("ostь") || x.endsWith("nostь")) return "ostь";
    if (x.endsWith("ьje") || x.endsWith("je")) return "je";
    if (x.endsWith("stvo")) return "stvo";
    if (x.endsWith("ь")) return "soft";
    if (x.endsWith("a")) return "a";
    if (x.endsWith("o")) return "o";
    if (x.endsWith("e")) return "e";
    return "cons";
  }

  function addList(map, key, item) {
    const k = foldPl(key);
    if (!k) return;
    const arr = map.get(k) || [];
    arr.push(item);
    arr.sort((a, b) => (b.priority || 0) - (a.priority || 0));
    map.set(k, arr.slice(0, 20));
  }

  function addLemma(polish, slovian, meta, priority) {
    const p = String(polish || "").trim();
    const s = String(slovian || "").trim();
    if (!p || !s || p.includes(" ") || s.includes(" ") || s.includes("..........")) return;
    const k = foldPl(p);
    const old = STATE.lemmas.get(k);
    const item = { pl: p, slo: s, g: inferGender(s, meta.g), a: meta.a || "inanimate", priority: priority || 0 };
    if (!old || item.priority > old.priority) STATE.lemmas.set(k, item);
  }

  function buildPatterns(rows) {
    let current = null;

    function close() {
      if (!current || !current.nom || current.forms.size < 5) return;
      current.g = inferGender(current.nom.slo, current.nom.meta.g);
      current.a = current.nom.meta.a || "inanimate";
      current.plClass = plClass(current.nom.pl);
      current.sloClass = sloClass(current.nom.slo);
      current.transforms = new Map();
      current.forms.forEach((form, k) => {
        current.transforms.set(k, makeTransform(current.nom.slo, form.slo));
      });
      STATE.patterns.push(current);
    }

    rows.forEach((row, index) => {
      if (!row || !row.polish || !row.slovian) return;
      const meta = parseMeta(row["type and case"]);
      if (!meta.noun || !meta.c || !meta.n) return;
      const pl = String(row.polish).trim();
      const slo = String(row.slovian).trim();
      if (!pl || !slo || pl.includes(" ") || slo.includes(" ")) return;

      if (meta.c === "nominative" && meta.n === "singular") {
        close();
        current = { nom: { pl, slo, meta, index }, forms: new Map() };
      }
      if (current) current.forms.set(slot(meta.c, meta.n), { pl, slo, meta, index });
    });

    close();
  }

  function scorePattern(lemma, pattern) {
    let score = 0;
    if (lemma.g === pattern.g) score += 800;
    if (lemma.a === pattern.a) score += 100;
    if (plClass(lemma.pl) === pattern.plClass) score += 320;
    if (sloClass(lemma.slo) === pattern.sloClass) score += 520;
    score += Math.min(commonSuffix(lemma.pl, pattern.nom.pl, foldPl), 8) * 25;
    score += Math.min(commonSuffix(lemma.slo, pattern.nom.slo, foldSlo), 8) * 35;
    if (foldSlo(lemma.slo) === foldSlo(pattern.nom.slo)) score += 2000;
    return score;
  }

  function choosePattern(lemma) {
    let best = null;
    let bestScore = -Infinity;
    for (const pattern of STATE.patterns) {
      const score = scorePattern(lemma, pattern);
      if (score > bestScore) {
        best = pattern;
        bestScore = score;
      }
    }
    return best;
  }

  function fallbackSlovian(lemma, c, n) {
    const w = lemma.slo;
    const g = lemma.g || inferGender(w);
    const a = lemma.a || "inanimate";

    if (n === "plural") {
      if (c === "nominative") {
        if (w.endsWith("ь")) return w.slice(0, -1) + "i";
        if (g === "neuter" && w.endsWith("o")) return w.slice(0, -1) + "a";
        if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "y";
        return w + "i";
      }
      if (c === "accusative") {
        if (a === "animate") return fallbackSlovian(lemma, "genitive", "plural");
        if (g === "neuter" && w.endsWith("o")) return w.slice(0, -1) + "a";
        if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "y";
        return w + "y";
      }
      if (c === "genitive") {
        if (w.endsWith("ь")) return w.slice(0, -1) + "ьji";
        if (w.endsWith("a") || w.endsWith("o")) return w.slice(0, -1);
        return w;
      }
      if (c === "locative") {
        if (w.endsWith("ь")) return w.slice(0, -1) + "ih";
        if (w.endsWith("ьje") || w.endsWith("je")) return w.slice(0, -1) + "ih";
        if (w.endsWith("stvo")) return w.slice(0, -1) + "ěh";
        if (g === "masculine") return w + "ěh";
        if (g === "neuter" && w.endsWith("o")) return w.slice(0, -1) + "ěh";
        if (w.endsWith("a")) return w.slice(0, -1) + "ah";
        return w + "ah";
      }
      if (c === "dative") {
        if (w.endsWith("ь")) return w.slice(0, -1) + "im";
        if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "am";
        return w + "om";
      }
      if (c === "instrumental") {
        if (w.endsWith("ь")) return w + "mi";
        if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "ami";
        return w + "y";
      }
      if (c === "vocative") return fallbackSlovian(lemma, "nominative", "plural");
    }

    if (c === "nominative") return w;
    if (c === "accusative") {
      if (g === "masculine" && a === "animate") return fallbackSlovian(lemma, "genitive", "singular");
      if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "ǫ";
      return w;
    }
    if (c === "genitive") {
      if (w.endsWith("ь")) return w.slice(0, -1) + "i";
      if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "y";
      if (g === "neuter" && w.endsWith("o")) return w.slice(0, -1) + "a";
      return w + "a";
    }
    if (c === "locative") {
      if (w.endsWith("ь")) return w.slice(0, -1) + "i";
      if (w.endsWith("ьje") || w.endsWith("je")) return w.slice(0, -1) + "i";
      if (w.endsWith("stvo")) return w.slice(0, -1) + "ě";
      if (g === "masculine") return w + "ě";
      if (g === "neuter" && w.endsWith("o")) return w.slice(0, -1) + "ě";
      if (g === "feminine" && w.endsWith("ga")) return w.slice(0, -2) + "dzě";
      if (g === "feminine" && w.endsWith("ka")) return w.slice(0, -2) + "cě";
      if (g === "feminine" && w.endsWith("ca")) return w.slice(0, -1) + "i";
      if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "ě";
      return w;
    }
    if (c === "dative") {
      if (w.endsWith("ь")) return w.slice(0, -1) + "i";
      if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "ě";
      if (g === "neuter" && w.endsWith("o")) return w.slice(0, -1) + "u";
      return w + "u";
    }
    if (c === "instrumental") {
      if (w.endsWith("ь")) return w + "jǫ";
      if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "ojǫ";
      if (g === "neuter" && w.endsWith("o")) return w.slice(0, -1) + "omь";
      return w + "omь";
    }
    if (c === "vocative") {
      if (g === "masculine" && !/[ьaeo]$/.test(w)) return w + "e";
      if (g === "feminine" && w.endsWith("a")) return w.slice(0, -1) + "o";
      return w;
    }
    return w;
  }

  function inflectSlovian(lemma, c, n) {
    const pattern = choosePattern(lemma);
    const tr = pattern && pattern.transforms.get(slot(c, n));
    if (tr) {
      const v = applyTransform(lemma.slo, tr);
      if (v) return v;
    }
    return fallbackSlovian(lemma, c, n);
  }

  function guessSloLemmaFromPolish(plLemma) {
    return normalize(plLemma)
      .replace(/ą/g, "ǫ")
      .replace(/ę/g, "ę")
      .replace(/ł/g, "l")
      .replace(/ń/g, "n")
      .replace(/ó/g, "o")
      .replace(/ś/g, "s")
      .replace(/ź|ż/g, "ž")
      .replace(/ć/g, "tь")
      .replace(/cz/g, "č")
      .replace(/sz/g, "š");
  }

  function inferUnknownLemma(word, wantedCase, wantedNumber) {
    const raw = normalize(word);
    const f = foldPl(word);
    const candidates = [];
    const add = (pl, g) => {
      if (!pl) return;
      const slo = guessSloLemmaFromPolish(pl);
      candidates.push({ pl, slo, g: g || inferGender(slo), a: "inanimate", priority: 10, inferred: true });
    };

    if (wantedCase === "genitive" && wantedNumber !== "plural") {
      if (f.endsWith("dla")) add(raw.slice(0, -2) + "ło", "neuter");
      if (f.endsWith("la")) add(raw.slice(0, -1) + "o", "neuter");
      if (f.endsWith("a")) add(raw.slice(0, -1), "masculine");
    }

    if (wantedCase === "dative" && wantedNumber !== "plural") {
      if (f.endsWith("dlu")) add(raw.slice(0, -2) + "ło", "neuter");
      if (f.endsWith("lu")) add(raw.slice(0, -1) + "o", "neuter");
    }

    if (wantedCase === "instrumental" && wantedNumber !== "plural") {
      if (f.endsWith("dlem")) add(raw.slice(0, -3) + "ło", "neuter");
      if (f.endsWith("lem")) add(raw.slice(0, -2) + "o", "neuter");
    }

    if (wantedCase === "locative" && wantedNumber !== "plural") {
      if (f.endsWith("dle")) add(raw.slice(0, -2) + "ło", "neuter");
      if (f.endsWith("le")) add(raw.slice(0, -1) + "o", "neuter");
      if (f.endsWith("scie")) add(raw.slice(0, -4) + "asto", "masculine");
    }

    if (wantedNumber === "plural" || /(ach|ech|om|ami|mi|ów|ow)$/.test(f)) {
      if (f.endsWith("dlach")) add(raw.slice(0, -4) + "ło", "neuter");
      if (f.endsWith("lach")) add(raw.slice(0, -3) + "o", "neuter");
      if (f.endsWith("dlom")) add(raw.slice(0, -3) + "ło", "neuter");
      if (f.endsWith("dlami")) add(raw.slice(0, -5) + "ło", "neuter");
    }

    return candidates[0] || null;
  }

  function detectNumber(word, wantedCase) {
    const f = foldPl(word);
    if (/(ach|ech|om|ami|mi|ów|ow)$/.test(f)) return "plural";
    return "singular";
  }

  function findCandidate(word, wantedCase, wantedNumber) {
    const k = foldPl(word);
    const exact = STATE.exact.get(k) || [];
    let best = null;
    let score = -Infinity;

    for (const item of exact) {
      let s = item.priority || 0;
      if (wantedCase && item.c === wantedCase) s += 1000;
      if (wantedNumber && item.n === wantedNumber) s += 300;
      if (item.exact) s += 500;
      if (s > score) { best = item; score = s; }
    }

    if (best && best.target) return best;

    let lemma = STATE.lemmas.get(k) || null;
    if (!lemma) lemma = inferUnknownLemma(word, wantedCase, wantedNumber);
    if (!lemma) return null;

    const c = wantedCase || "nominative";
    const n = wantedNumber || detectNumber(word, c);
    return { target: inflectSlovian(lemma, c, n), c, n, lemma, exact: false, priority: lemma.priority || 0 };
  }

  function splitWordToken(token) {
    const m = String(token || "").match(/^([^\p{L}\p{M}0-9'’]*)([\p{L}\p{M}0-9'’]+)([^\p{L}\p{M}0-9'’]*)$/u);
    if (!m) return { pre: "", core: token, post: "", isWord: false };
    return { pre: m[1] || "", core: m[2] || "", post: m[3] || "", isWord: true };
  }

  function copyCase(source, target) {
    const s = String(source || "");
    const t = String(target || "");
    if (!t) return t;
    if (s.length > 1 && s === s.toLocaleUpperCase("pl")) return t.toLocaleUpperCase("pl");
    if (s[0] && s[0] === s[0].toLocaleUpperCase("pl") && s[0] !== s[0].toLocaleLowerCase("pl")) return t.charAt(0).toLocaleUpperCase("pl") + t.slice(1);
    return t;
  }

  function fixSpacing(text) {
    return String(text || "")
      .replace(/\s+([,.;:!?%])/g, "$1")
      .replace(/([([{„«])\s+/g, "$1")
      .replace(/\s+([)\]}”»])/g, "$1")
      .replace(/\s+/g, " ")
      .trim();
  }

  function translateText(input) {
    const parts = String(input || "").trim().split(/(\s+)/).filter(x => x !== "");
    const out = [];
    let changed = false;

    for (let i = 0; i < parts.length; i++) {
      if (/^\s+$/.test(parts[i])) { out.push(parts[i]); continue; }

      const cur = splitWordToken(parts[i]);
      if (!cur.isWord) { out.push(parts[i]); continue; }

      const prepKey = normalize(cur.core);
      if (PREP_CASE.has(prepKey)) {
        let j = i + 1;
        const spaces = [];
        while (j < parts.length && /^\s+$/.test(parts[j])) { spaces.push(parts[j]); j++; }
        if (j < parts.length) {
          const next = splitWordToken(parts[j]);
          if (next.isWord) {
            const wantedCase = PREP_CASE.get(prepKey);
            const wantedNumber = detectNumber(next.core, wantedCase);
            const cand = findCandidate(next.core, wantedCase, wantedNumber);
            if (cand) {
              out.push(cur.pre + copyCase(cur.core, PREP_SLO.get(prepKey) || cur.core));
              out.push(spaces.join("") || " ");
              out.push(next.pre + copyCase(next.core, cand.target) + next.post);
              i = j;
              changed = true;
              continue;
            }
          }
        }
      }

      const cand = findCandidate(cur.core, null, null);
      if (cand) {
        out.push(cur.pre + copyCase(cur.core, cand.target) + cur.post);
        changed = true;
      } else {
        out.push(parts[i]);
      }
    }

    const result = fixSpacing(out.join(""));
    return { result, changed };
  }

  async function fetchJson(path) {
    try {
      const res = await fetch(path, { cache: "no-store" });
      if (!res.ok) return [];
      const text = await res.text();
      if (!text.trim()) return [];
      return JSON.parse(text);
    } catch (e) {
      return [];
    }
  }

  async function load() {
    if (STATE.loaded) return;
    if (STATE.loading) return STATE.loading;

    STATE.loading = (async function () {
      const vuzor = await fetchJson("vuzor.json");
      const osnova = await fetchJson("osnova.json");
      const rows = [];

      if (Array.isArray(vuzor)) {
        buildPatterns(vuzor);
        vuzor.forEach((row, index) => rows.push({ row, priority: 3000 - index / 100000 }));
      }
      if (Array.isArray(osnova)) {
        osnova.forEach((row, index) => rows.push({ row, priority: 1500 - index / 100000 }));
      }

      rows.forEach(({ row, priority }) => {
        if (!row || !row.polish || !row.slovian) return;
        const meta = parseMeta(row["type and case"]);
        if (!meta.noun) return;
        if (meta.c && meta.n) {
          addList(STATE.exact, row.polish, {
            source: row.polish,
            target: row.slovian,
            c: meta.c,
            n: meta.n,
            g: inferGender(row.slovian, meta.g),
            a: meta.a || "inanimate",
            exact: true,
            priority
          });
        }
        if (meta.c === "nominative" && meta.n === "singular") addLemma(row.polish, row.slovian, meta, priority);
      });

      STATE.loaded = true;
      window.SlovoDeclensionPatch = { translate: translateText, state: STATE };
    })();

    return STATE.loading;
  }

  function getOutput() {
    const o = $(IDS.output);
    if (!o) return "";
    return o.value !== undefined ? o.value : o.textContent;
  }

  function setOutput(text) {
    const o = $(IDS.output);
    if (!o) return;
    if (o.value !== undefined) o.value = text;
    else o.textContent = text;
  }

  function hideSuggestion() {
    const box = $(IDS.sugg);
    if (!box) return;
    box.innerHTML = "";
    box.hidden = true;
    box.style.setProperty("display", "none", "important");
  }

  function shouldOverride(oldOutput, translated) {
    if (!translated.changed) return false;
    const old = String(oldOutput || "");
    if (!old.trim()) return true;
    if (old.includes("🔴") || old.includes("●") || old.includes("?") || old.includes("undefined")) return true;
    return true;
  }

  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(async function () {
      const input = $(IDS.input);
      const src = $(IDS.src);
      const tgt = $(IDS.tgt);
      if (!input || !src || !tgt || src.value !== "pl" || tgt.value !== "slo") return;

      hideSuggestion();
      await load();

      setTimeout(function () {
        hideSuggestion();
        const translated = translateText(input.value);
        const old = getOutput();
        if (shouldOverride(old, translated)) setOutput(translated.result);
      }, 180);
    }, 100);
  }

  function install() {
    const style = document.createElement("style");
    style.textContent = "#suggestionBox{display:none!important;visibility:hidden!important;height:0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important;}";
    document.head.appendChild(style);
    hideSuggestion();

    document.addEventListener("input", e => { if (e.target && e.target.id === IDS.input) schedule(); }, true);
    document.addEventListener("paste", e => { if (e.target && e.target.id === IDS.input) setTimeout(schedule, 0); }, true);
    document.addEventListener("change", e => { if (e.target && [IDS.input, IDS.src, IDS.tgt].includes(e.target.id)) schedule(); }, true);

    load().then(schedule);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", install);
  else install();
})();
