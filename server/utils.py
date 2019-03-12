__author__ = 'rcj1492'
__created__ = '2018.04'

def construct_response(request_details, request_model=None, endpoint_list=None, ignore_errors=False, check_session=False):

# import dependencies
    from labpack.records.id import labID
    from labpack.parsing.flask import validate_request_content

# construct default response
    record_id = labID()
    response_details = {
        'dt': record_id.epoch,
        'id': record_id.id36,
        'code': 200,
        'error': '',
        'details': {}
    }

# validate request format
    if ignore_errors:
        return response_details
    if request_details['error']:
        response_details['error'] = request_details['error']
        response_details['code'] = request_details['code']
        return response_details
    if endpoint_list:
        from os import path
        route_root, route_endpoint = path.split(request_details['route'])
        if not route_endpoint in endpoint_list:
            from labpack.parsing.grammar import join_words
            response_details['error'] = 'request endpoint must be one of %s' % join_words(endpoint_list)
            response_details['code'] = 400
            return response_details
    if check_session:
        if not request_details['session']:
            response_details['error'] = 'request missing valid session token'
            response_details['code'] = 400
            return response_details
    if request_model:
        if not request_details['json']:
            response_details['error'] = 'request body must be content-type application/json'
            response_details['code'] = 400
        else:
            status_details = validate_request_content(request_details['json'], request_model)
            if status_details['error']:
                response_details['error'] = status_details['error']
                response_details['code'] = status_details['code']

    return response_details

def send_email(email_client, user_email, user_name):
    
# define reference links
    html_template = 'emails/alert.html'

# define email kwargs
    html_kwargs = {
        'base_url': 'http://localhost:5000',
        'application_logo': 'https://lyvia.herokuapp.com/public/images/logos/lab-logo1.png',
        'application_name': 'Lyvia',
        'application_address': 'One Broadway, 5th Floor, Cambridge, MA 02142',
        'user_name': user_name
    }

# construct email html
    from flask import render_template
    email_html = render_template(html_template, **html_kwargs)

# send email
    email_subject = 'Sleep Disruptions Detected for %s' % user_name
    email_kwargs = {
        'recipient_list': [ user_email ], 
        'sender_email': 'lyvia@collectiveacuity.com',
        'sender_name': 'Lyvia',
        'email_subject': email_subject,
        'content_html': email_html
    }
    email_client.send_email(**email_kwargs)

if __name__ == '__main__':
    
# construct flask context
    import json
    from flask import Flask
    flask_app = Flask(import_name=__name__, static_folder='public', template_folder='views')
    request_kwargs = {
        'method': 'GET'
    }


# construct email client
    with flask_app.test_request_context('/', **request_kwargs) as ctx:
        from server.init import email_client
        user_name = 'Charlotte'
        user_email = 'support@collectiveacuity.com'
        send_email(email_client, user_email, user_name)