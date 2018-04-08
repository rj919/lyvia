__author__ = 'rcj1492'
__created__ = '2018.04'

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# initialize app
from flask import Flask, jsonify, render_template, request, Response
flask_kwargs = {
    'import_name': __name__,
    'static_folder': 'public',
    'template_folder': 'views'
}
app = Flask(**flask_kwargs)

# initialize logging and debugging
import logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.config['ASSETS_DEBUG'] = False

# add cross origin support
from flask_cors import CORS
CORS(app)

# construct the landing page
@app.route('/')
def landing_page():
    return render_template('dashboard.html'), 200