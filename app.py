from flask import Flask, render_template_string, request
from logic import translator

app = Flask(__name__)

# Szablon HTML/CSS wewnątrz pliku dla wygody
HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Słowiański Tłumacz AI</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; padding-top: 50px; }
        .container { width: 700px; background: #161b22; padding: 30px; border-radius: 12px; border: 1px solid #30363d; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
        h1 { color: #58a6ff; font-size: 24px; margin-bottom: 20px; }
        textarea { width: 100%; height: 120px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #e6edf3; padding: 15px; font-size: 16px; box-sizing: border-box; }
        button { background: #238636; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 15px; width: 100%; }
        button:hover { background: #2ea043; }
        .output { margin-top: 25px; padding: 20px; background: #010409; border-radius: 6px; border-left: 4px solid #58a6ff; font-size: 1.3em; color: #ffa657; min-height: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Slovian Translator (NSS)</h1>
        <form method="POST">
            <textarea name="text" placeholder="Wpisz polskie zdanie..."></textarea>
            <button type="submit">REKONSTRUUJ</button>
        </form>
        {% if result %}
        <div class="output">
            <strong>Rezultat:</strong><br>
            {{ result }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        user_input = request.form.get('text', '')
        result = translator.translate_sentence(user_input)
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
