from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    original = ""
    result = ""
    
    if request.method == 'POST':
        original = request.form.get('content', '').strip()
        if original:
            # bardzo prosta zamiana – przykład
            result = re.sub(r'ą', 'ǫ', original)
            result = re.sub(r'ę', 'ę', result)
            result = re.sub(r'rz', 'rь', result)
            result = re.sub(r'[sz]', 'š', result)  # uproszczenie
    
    return render_template('index.html', original=original, result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
