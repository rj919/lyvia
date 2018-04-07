__author__ = 'rcj1492'
__created__ = '2018.04'

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# initialize app
from flask import Flask, jsonify, render_template
flask_kwargs = {
    'import_name': __name__,
    'static_folder': 'public',
    'template_folder': 'views'
}
app = Flask(**flask_kwargs)

# initialize logging and debugging
import sys
import logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.config['ASSETS_DEBUG'] = False

# add cross origin support
from flask_cors import CORS
CORS(app)

# construct the landing page
from labpack.records.settings import load_settings
api_model = load_settings('models/api.json')
@app.route('/')
def landing_page():
    return jsonify(api_model['schema']), 200

# construct the catchall for URLs which do not exist
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# initialize test wsgi localhost server with default memory job store
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    app.logger.info('Server started.')
    http_server.serve_forever()
    # app.run(host='0.0.0.0', port=5001)

