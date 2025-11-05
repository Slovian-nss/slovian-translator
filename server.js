import express from 'express';
import cors from 'cors';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import OpenAI from 'openai';
import 'dotenv/config';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));

// Serve everything from root (no folders needed)
app.use(express.static(__dirname));

// Health
app.get('/healthz', (req, res) => res.json({ ok: true }));

// Root -> index.html (in repo root)
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// OpenAI client
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const MODEL = process.env.OPENAI_MODEL || 'gpt-4o';

// Load dictionary from root slovnik.json
const slovnikPath = path.join(__dirname, 'slovnik.json');
let ENTRIES = [];
try {
  const txt = await fs.readFile(slovnikPath, 'utf8');
  ENTRIES = JSON.parse(txt);
} catch (e) {
  console.error('Cannot load slovnik.json:', e);
  ENTRIES = [];
}

// Quick index for single-word lookups
const SINGLE = new Map();
for (const e of ENTRIES) {
  const key = (e.pl || '').trim().toLowerCase();
  if (key && !key.includes(' ')) SINGLE.set(key, e);
}
const WORD_RE = /(\p{L}+|[\d]+|[\s]+|[^\w\s]+)/gu;
function tokenize(s) { const out=[]; let m; while((m=WORD_RE.exec(s))!==null) out.push(m[0]); return out; }
function collectHits(text, maxHits = 600) {
  const words = tokenize(text).filter(t => /\p{L}/u.test(t)).map(t => t.toLowerCase());
  const uniq = Array.from(new Set(words));
  const hits = [];
  for (const w of uniq) { const e = SINGLE.get(w); if (e) hits.push(e); if (hits.length >= maxHits) break; }
  return hits;
}

// API translate
app.post('/api/translate', async (req, res) => {
  try {
    const { text } = req.body || {};
    if (typeof text !== 'string' || !text.trim()) {
      return res.status(400).json({ error: 'Provide non-empty `text` string.' });
    }
    const mini = collectHits(text, 600).map(({pl, sl, tag}) => ({ pl, sl, tag }));
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
              properties: { src:{type:"string"}, dst:{type:"string"}, note:{type:"string"} },
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
      "1) Prefer dictionary mappings. 2) Use idioms from dict. 3) Apply project conventions (e.g., `vu` + locative). 4) If missing, adapt Polish roots. 5) Return JSON only."
    ].join('\n');
    const user = JSON.stringify({ text, dictionary_hits: mini });

    const resp = await openai.responses.create({
      model: MODEL,
      input: [{ role: "system", content: sys }, { role: "user", content: user }],
      response_format: { type: "json_schema", json_schema },
      temperature: 0.2,
      max_output_tokens: 800
    });

    const content = resp.output?.[0]?.content?.[0]?.text || resp.output_text || "";
    let data; try { data = JSON.parse(content); } catch { data = { translation: content }; }
    res.json({ ok: true, model: MODEL, data });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || 'Internal error' });
  }
});

const port = process.env.PORT || 8787;
app.listen(port, () => console.log(`Perkladar agent listening on http://localhost:${port}`));
