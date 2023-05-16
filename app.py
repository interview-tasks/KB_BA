from flask import Flask, render_template, request
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    if text:
        return text
    else:
        return 'empty'
