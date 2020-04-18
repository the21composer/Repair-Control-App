from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/worker')
def worker():
    return render_template('worker.html')

@app.route('/site')
def site():
    return render_template('site_manager.html')

@app.route('/repair')
def repair():
    return render_template('repair_manager.html')

@app.route('/foreman')
def foreman():
    return render_template('foreman.html') 