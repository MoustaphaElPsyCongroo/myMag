# #!/usr/bin/python3
"""Google Auth"""
from api.v1.views import app_views
from decouple import config
from functools import wraps
import requests
from models import storage
from models.user import User
from flask import jsonify, request
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import pathlib

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, 'client-secret.json')
algorithm = config('JWT_ENCODE_ALGORITHM')
BACKEND_URL = config('BACKEND_URL')
FRONTEND_URL = config('FRONTEND_URL')


def get_expired_token_user(refresh_token):
    """Refreshes an expired id_token, retrieving the corresponding user's
      id and new token
    """
    data = {
        'refresh_token': refresh_token,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }

    try:
        res = requests.post(
            'https://oauth2.googleapis.com/token', data=data)
    except Exception as e:
        return (None, None)

    if res.status_code != 200:
        return (None, None)

    res = res.json()

    new_token = res['id_token']
    try:
        id_info = id_token.verify_oauth2_token(
            new_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10)
    except Exception as e:
        return (None, None)

    user_id = id_info.get('sub')
    return (user_id, new_token)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Decorator to ask for a token in exchange for an API resource,
          in the manner of Flask-Login"""
        token = None
        user_id = None
        expires_in = 9999
        if (request.headers.get('Authorization')
                and request.headers.get('Refreshing')):
            token = request.headers.get(
                'Authorization').split('Bearer ')[1]
        if token is None:
            return jsonify({
                'error': 'Missing token'
            }), 401

        id_info = {}
        try:
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10)
        except Exception as e:
            expires_in = 0
        user_id = id_info.get('sub')

        # Expired token: refresh it
        if expires_in < 50:
            refresh_token = request.headers.get(
                'Refreshing').split('RefreshToken ')[1]
            user_id, token = get_expired_token_user(refresh_token)

            if user_id is None:
                return jsonify({
                    'error': "Can't authenticate user"
                }), 401

        found = storage.get(User, user_id)
        if found is None:
            return jsonify({
                'error': 'Unauthorized'
            }), 401
        return f(token, found, *args, **kwargs)
    return decorated_function


@app_views.route('/auth/login', methods=['POST'])
def login():
    """Google Auth flow, decoding and verifying an id_token"""
    token = None
    user_id = None
    expires_in = 9999
    if (request.headers.get('Authorization')
            and request.headers.get('Refreshing')):
        token = request.headers.get(
            'Authorization').split('Bearer ')[1]
    if token is None:
        return jsonify({
            'error': 'Missing token'
        }), 401
    print('token', token)

    id_info = {}

    try:
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10)
    except Exception as e:
        expires_in = 0
    user_id = id_info.get('sub')

    # Expired token: refresh it
    if expires_in < 50:
        refresh_token = request.headers.get(
            'Refreshing').split('RefreshToken ')[1]
        user_id, token = get_expired_token_user(refresh_token)

        if user_id is None:
            return jsonify({
                'error': "Can't authenticate user"
            }), 401

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

    return jsonify(
        id=user_id,
        name=user_name,
        email=user_email,
        profile_pic=user_picture
    ), 200
