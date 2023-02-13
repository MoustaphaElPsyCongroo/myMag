#!/usr/bin/python3
"""Flask Application"""
import os
from decouple import config
from models import storage
from models.user import User
from api.v1.views import app_views
from flask_cors import CORS
from flasgger import Swagger
import requests
from flask import Flask, abort, jsonify, redirect, request, session
import google
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import json
import jwt
from oauthlib.oauth2 import WebApplicationClient
import pathlib


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
app.secret_key = os.urandom(24)
# cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'


@app.teardown_appcontext
def close_db(error):
    """Close Storage"""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """ 404 Error
    ---
    responses:
      404:
        description: a resource was not found
    """
    status = {
        'error': 'Not found'
    }

    return jsonify(status), 404


app.config['SWAGGER'] = {
    'title': 'myMag RESTful API',
    'uiversion': 3
}

Swagger(app)


GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, 'client-secret.json')
algorithm = config('JWT_ENCODE_ALGORITHM')
BACKEND_URL = config('BACKEND_URL')
FRONTEND_URL = config('FRONTEND_URL')

# Bypass http warnings ---- IN TESTING ONLY, NEVER IN PRODUCTION ---
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

"""Find what URL to redirect to for Google login
    and what user information to retrieve
"""
# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=[
#         'https://www.googleapis.com/auth/userinfo.profile',
#         'https://www.googleapis.com/auth/userinfo.email',
#         'openid'],
#     redirect_uri=f'{BACKEND_URL}/login/callback'
# )


def login_required(function):
    def wrapper(*args, **kwargs):
        """Decorator for auth validation, in the example of Flask-Login"""
        encoded_jwt = None
        if (request.headers.get('Authorization')):
            encoded_jwt = request.headers.get(
                'Authorization').split('Bearer ')[1]
        if encoded_jwt is None:
            return jsonify({
                'message': 'Unauthorized'
            }), 401
        else:
            return function()
    return wrapper


def Generate_JWT(payload):
    """Generate a JSON Web Token"""
    encoded_jwt = jwt.encode(payload, app.secret_key, algorithm=algorithm)
    return encoded_jwt


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    auth_code = request.get_json()['code']

    data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    res = requests.post('https://oauth2.googleapis.com/token', data=data)

    id_info = id_token.verify_oauth2_token(
        res.data.id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
    user_id = id_info.get('sub')
    user_name = id_info.get('name')
    user_email = id_info.get('email')
    user_picture = id_info.get('picture')

    found = storage.get(User, user_id)

    if found is None:
        new_user = User(
            id=user_id,
            name=user_name,
            email=user_email,
            profile_pic=user_picture
        )
        storage.new(new_user)
        storage.save()

    return jsonify({
        'id': user_id,
        'name': user_name,
        'email': user_email,
        'profile_pic': user_picture,
        'access_token': res.data.access_token,
        'refresh_token': res.data.refresh_token
    }), 200


@ app.route('/api/v1/auth/refresh', methods=['POST'])
def refresh():
    refresh_token = request.get_json()['code']

    data = {
        'refresh_token': refresh_token,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }

    res = requests.post('https://oauth2.googleapis.com/token', data=data)

    print('res: ', res.json())
    return jsonify(res.json()), 200


# @app.route('/api/v1/login/callback')
# def callback():
#     """Get auth code sent back from Google and get token"""
#     flow.fetch_token(authorization_response=request.url)
#     credentials = flow.credentials
#     request_session = requests.session()
#     token_request = google.auth.transport.requests.Request(
#         session=request_session)

#     id_info = id_token.verify_oauth2_token(
#         id_token=credentials._id_token,
#         request=token_request,
#         audience=GOOGLE_CLIENT_ID,
#         clock_skew_in_seconds=3
#     )
#     session['google_id'] = id_info.get('sub')

#     del id_info['aud']
#     jwt_token = Generate_JWT(id_info)

#     user_id = id_info.get('sub')
#     user_name = id_info.get('name')
#     user_email = id_info.get('email')
#     user_picture = id_info.get('picture')
#     user = storage.get(User, user_id)

#     if user is None:
#         new_user = User(
#             id=user_id,
#             name=user_name,
#             email=user_email,
#             profile_pic=user_picture
#         )
#         storage.new(new_user)
#         storage.save()
#     # return redirect(f'{FRONTEND_URL}?jwt={jwt_token}')
#     return jsonify({'JWT': json.dumps(jwt_token)}), 200


# @app.route('/api/v1/auth/google')
# def login():
#     """Get Google's authorization url and store the state so that
#     the callback can verify the auth server response
#     """
#     authorization_url, state = flow.authorization_url()
#     session['state'] = state
#     return jsonify({'auth_url': authorization_url}), 200


# @app.route('/api/v1/logout')
# def logout():
#     """Clear user's id from the flask session
#     """
#     # Don't forget to clear the localStorage from the frontend
#     session.clear()
#     return jsonify({'message': 'User successfully logged out'}), 202


# # A remplacer par la route User quand on la fera puis suppirmer celle la,
# # c'est juste pour tester
# # Euh, quoique… A voir quand j'aurai testé depuis React
# @app.route('/api/v1/home')
# @login_required
# def home_page_user():
#     # encoded_jwt = request.headers.get('Authorization').split('Bearer')[1]
#     # decoded_jwt = jwt.decode(
#     #     encoded_jwt, app.secret_key, algorithm=algorithm)
#     user = storage.get(User, session['google_id'])
#     if user is not None:
#         user_id = user.id
#         user_email = user.email
#         user_name = user.name
#         user_picture = user.profile_pic

#     return jsonify({
#         'user_id': user_id,
#         'user_email': user_email,
#         'user_name': user_name,
#         'user_picture': user_picture
#     }), 200


if __name__ == "__main__":
    """Main Function"""
    host = config('MYMAG_API_HOST')
    port = config('MYMAG_API_PORT')
    if not host:
        host = '0.0.0.0'
    if not port:
        port = '5000'
    app.run(host=host, port=port, threaded=True)
