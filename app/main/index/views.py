from flask import render_template

from . import index

# http://127.0.0.1:5000/consent/
@index.route('/')
def index():
    return render_template('index.html')