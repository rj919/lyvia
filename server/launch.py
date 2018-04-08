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

# import data objects
from labpack.records.time import labDT
from server.init import sql_tables, telemetry_model, api_model, email_client

# import route dependencies
import json
from server.utils import construct_response
from labpack.parsing.flask import extract_request_details

# construct the landing page
@app.route('/')
def landing_page():
    return jsonify(api_model['schema']), 200

# construct users routes
@app.route('/users', methods=['GET'])
def users_route():

    # ingest request
    request_details = extract_request_details(request)
    app.logger.debug(request_details)
    response_details = construct_response(request_details)
    user_list = []
    for record in sql_tables['users'].list():
        user_list.append(record)
    response_details['details'] = user_list
    app.logger.debug(response_details)
    return jsonify(response_details), response_details['code']

# construct telemetry routes
@app.route('/telemetry', methods=['GET','POST'])
def telemetry_route():

    # ingest request
    request_details = extract_request_details(request)
    app.logger.debug(request_details)
    call_on_close = None
    
    # handle get telemetry
    if request_details['method'] == 'GET':
        response_details = construct_response(request_details)
        user_id = request_details['params'].get('user')
        start_date = request_details['params'].get('start')
        end_date = request_details['params'].get('end')
        telemetry_list = []
        if user_id and start_date and end_date:
            query_criteria = {
                '.user_id': { 'equal_to': user_id },
                '.date': {
                    'min_value': start_date,
                    'max_value': end_date
                }
            }
            for record in sql_tables['telemetry'].list(query_criteria):
                telemetry_list.append(record)
        else:
            for record in sql_tables['telemetry'].list():
                telemetry_list.append(record)
        response_details['details'] = telemetry_list
        app.logger.debug(response_details)
        return jsonify(response_details), response_details['code']

    # handle post telemetry
    if request_details['method'] == 'POST':
        response_details = construct_response(request_details, telemetry_model)
        if not response_details['error']:
            telemetry_dt = request_details['json']['dt']
            telemetry_record = {
                'date': labDT.fromEpoch(telemetry_dt).zulu()[0:10],
            }
            for key, value in request_details['json'].items():
                telemetry_record[key] = value
            telemetry_id = sql_tables['telemetry'].create(telemetry_record)
            response_details['details'] = { 'id': telemetry_id }

            # test for consistent anomalies
            if telemetry_record['anomalous']:
                user_id = telemetry_record['user_id']
                query_criteria = { 'user_id': user_id }
                sort_criteria = [ { '.dt': 'descend' } ]
                count = 0
                for record in sql_tables['telemetry'].list(query_criteria, sort_criteria):
                    if not record['anomalous']:
                        break
                    count += 1
                    if count > 2:
                        # send alert
                        from server.utils import send_email
                        def alert_user():
                            user_email = ''
                            user_name = ''
                            for user in sql_tables['users'].list({'user_id': user_id}):
                                user_email = user['email']
                                user_name = user['name']
                                break
                            send_email(email_client, user_email, user_name)
                        call_on_close = alert_user

        # compose response
        if call_on_close:
            response_kwargs = {
                'response': json.dumps(response_details),
                'status': response_details['code'],
                'mimetype': 'application/json'
            }
            response_object = Response(**response_kwargs)
            response_object.call_on_close(call_on_close)
            app.logger.debug(response_details)
            return response_object

        else:
            app.logger.debug(response_details)
            return jsonify(response_details), response_details['code']

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

