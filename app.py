<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Slovian NSS | Model 2.0</title>
  <style>
    :root {
      --bg: #0d1117;
      --bg-dark: #010409;
      --text: #e6edf3;
      --text-light: #8b949e;
      --accent: #58a6ff;
      --accent-dark: #388bfd;
      --output: #ffa657;
      --border: #30363d;
      --btn: #238636;
      --btn-hover: #2ea043;
    }

    * { box-sizing: border-box; margin:0; padding:0; }

    body {
      background: var(--bg-dark);
      color: var(--text);
      font-family: system-ui, -apple-system, sans-serif;
      min-height: 100vh;          /* ← poprawione */
      padding: 1.5rem;
      line-height: 1.5;
    }

    .wrapper {
      max-width: 960px;
      margin: 0 auto;
    }

    header {
      text-align: center;
      margin: 0 0 2rem;
      color: var(--accent);
      font-size: 1.8rem;
      font-weight: 600;
      letter-spacing: -0.02em;
    }

    .card {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }

    textarea {
      width: 100%;
      min-height: 160px;
      background: var(--bg-dark);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem;
      font-size: 1.1rem;
      font-family: inherit;
      resize: vertical;
      margin: 1rem 0;
      transition: border-color 0.2s;
    }

    textarea:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(88,166,255,0.15);
    }

    .btn {
      background: var(--btn);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0.9rem 1.8rem;
      font-size: 1.05rem;
      font-weight: 600;
      cursor: pointer;
      width: 100%;
      transition: all 0.2s;
    }

    .btn:hover {
      background: var(--btn-hover);
      transform: translateY(-1px);
    }

    .output {
      margin-top: 2rem;
      background: rgba(255,166,87,0.08);
      border: 1px solid rgba(255,166,87,0.2);
      border-radius: 8px;
      padding: 1.5rem;
    }

    .output-label {
      color: var(--text-light);
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.8rem;
    }

    .result {
      color: var(--output);
      font-family: "JetBrains Mono", "Courier New", monospace;
      font-size: 1.25rem;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }

    @media (max-width: 600px) {
      body { padding: 1rem; }
      header { font-size: 1.5rem; }
      .card { padding: 1.2rem; }
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <header>Slovian NSS 2.0</header>

    <div class="card">
      <form method="POST">
        <textarea
          name="content"
          placeholder="Wpisz tekst po polsku..."
          autofocus
        >{{ original }}</textarea>
        <button type="submit" class="btn">REKONSTRUUJ FORMĘ</button>
      </form>
    </div>

    {% if result %}
    <div class="output">
      <div class="output-label">Prasłowiańska rekonstrukcja (NSS):</div>
      <div class="result">{{ result }}</div>
    </div>
    {% endif %}
  </div>
</body>
</html>
