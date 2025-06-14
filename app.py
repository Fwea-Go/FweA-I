from flask import Flask, render_template, send_from_directory
from whitenoise import WhiteNoise
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

@app.route('/')
def index():
    # Render the optimized Bandzoogle-ready index.html
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
