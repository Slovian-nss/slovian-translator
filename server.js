import express from 'express';
import cors from 'cors';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import OpenAI from 'openai';
import 'dotenv/config';

// --- paths / express ---------------------------------------------------------
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));

// Serwujemy statycznie wszystko z roota (bo wszystkie pliki leżą w katalogu głównym)
app.use(express.static(__dirname));

// Health
app.get('/healthz', (_req, res) => res.json({ ok: true }));

// Root -> index.html (leży w repo root)
app.get('/', (_req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// --- OpenAI client -----------------------------------------------------------
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const MODEL = process.env.OPENAI_MODEL || 'gpt-4o'; // np. gpt-4o-mini też OK

// --- Slovnik -----------------------------------------------------------------
const slovnikPath = path.join(__dirname, 'slovnik.json');

let ENTRIES = [];
(async () => {
  try {
    const txt = await fs.readFile(slovnikPath, 'utf8');
    ENTRIES = JSON.parse(txt);
    console.log(`Loaded slovnik.json entries: ${ENTRIES.length}`);
  } catch (e) {
    console.error('Cannot load slovnik.json:', e);
    ENTRIES = [];
  }
})();

// Szybki indeks dla haseł jednowyrazowych
const SINGLE = new Map();
function rebuildIndex() {
  SINGLE.clear();
  for (const e of ENTRIES) {
    const key = (e.pl || '').trim().toLowerCase();
    if (key && !key.includes(' ')) SINGLE.set(key, e);
  }
}
rebuildIndex();

const WORD_RE = /(\p{L}+|[\d]+|[\s]+|[^\w\s]+)/gu;
function tokenize(s) {
  const out = [];
  let m;
  while ((m = WORD_RE.exec(s)) !== null) out.push(m[0]);
  return out;
}
function collectHits(text, maxHits = 600) {
  const words = tokenize(text)
    .filter(t => /\p{L}/u.test(t))
    .map(t => t.toLowerCase());
  const uniq = Array.from(new Set(words));
  const hits = [];
  for (const w of uniq) {
    const e = SINGLE.get(w);
    if (e) hits.push(e);
    if (hits.length >= maxHits) break;
  }
  return hits;
}

// --- API: translate ----------------------------------------------------------
app.post('/api/translate', async (req, res) => {
  try {
    const { text } = req.body || {};
    if (typeof text !== 'string' || !text.trim()) {
      return res.status(400).json({ error: 'Provide non-empty `text` string.' });
    }

    // mikrowyciąg słów ze słownika do kontekstu
    const mini = collectHits(text, 600).map(({ pl, sl, tag }) => ({ pl, sl, tag }));

    const json_schema = {
      name: "SlovianTranslate",
      schema: {
        type: "object", additionalProperties: false,
        properties: {
          translation: { type: "string" },
          coverage_note: { type: "string" },
          tokens: {
            type: "array",
            items: {
              type: "object", additionalProperties: false,
              properties: {
                src: { type: "string" },
                dst: { type: "string" },
                note: { type: "string" }
              },
              required: ["src"]
            }
          }
        },
        required: ["translation"]
      }
    };

    const sys = [
      "You are GPT-5 Thinking, acting as the brain of Perkladarь slovjenьskogo ęzyka.",
      "Translate Polish → Slovian.",
      "1) Prefer dictionary mappings. 2) Use idioms from dict. 3) Apply project conventions (e.g., `vu` + locative). 4) If missing, adapt Polish roots. 5) Return JSON only that matches the schema."
    ].join('\n');

    const user = JSON.stringify({ text, dictionary_hits: mini });

    let data;

    // 1) Najpierw spróbuj Chat Completions z JSON-em (stabilne w wielu wersjach)
    try {
      const chat = await openai.chat.completions.create({
        model: MODEL,
        messages: [
          { role: "system", content: sys },
          { role: "user", content: user }
        ],
        response_format: { type: "json_object" },
        temperature: 0.2
      });
      const content = chat.choices?.[0]?.message?.content ?? "{}";
      data = JSON.parse(content);
    } catch (e1) {
      // 2) Fallback: Responses API (bez kontrowersyjnych parametrów), sami parse'ujemy
      const resp = await openai.responses.create({
        model: MODEL,
        input: [
          { role: "system", content: sys },
          { role: "user", content: user }
        ],
        temperature: 0.2,
        max_output_tokens: 800
      });

      // różne ścieżki w zależności od wersji SDK
      const content =
        resp.output_text ||
        (resp.output?.[0]?.content?.find?.(c => c.type === 'output_text')?.text) ||
        (resp.output?.[0]?.content?.[0]?.text) ||
        "";

      try {
        data = JSON.parse(content);
      } catch {
        data = { translation: content, coverage_note: "fallback: not strict JSON" };
      }
    }

    // odesłanie wyniku
    res.json({ ok: true, model: MODEL, data });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || 'Internal error' });
  }
});

// --- listen ------------------------------------------------------------------
const port = process.env.PORT || 8787;
app.listen(port, () =>
  console.log(`Perkladar agent listening on http://localhost:${port}`)
);
