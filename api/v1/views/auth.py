#!/usr/bin/python3
from decouple import config
from api.v1.views import app_views
import requests
from models import storage
from models.user import User
from flask import abort, jsonify, redirect, request
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
import json
from oauthlib.oauth2 import WebApplicationClient

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = config('GOOGLE_DISCOVERY_URL')

client = WebApplicationClient(GOOGLE_CLIENT_ID)


"""Get Google's provider configuration as required by OpenID Connect"""


def get_google_provider_cfg():
    try:
        req = requests.get(GOOGLE_DISCOVERY_URL)
        return req.json()
    except requests.ConnectionError as e:
        print('Connection error: ', str(e))
    except requests.Timeout as e:
        print('Timeout: ', str(e))
    except requests.RequestException as e:
        print('Request error: ', str(e))
    except KeyboardInterrupt:
        print('Program closed prematurely')


@app_views.route('/login')
def login():
    """Find what URL to redirect to for Google login"""
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']

    # Construct the request for Google login and provide scopes to retrieve
    # user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + '/callback',
        scope=['openid', 'email', 'profile']
    )
    return redirect(request_uri)


@app_views.route('/login/callback')
def callback():
    """Get authorization code sent back from Google and get token"""
    code = request.args.get('code')

    # Find what URL to get authorization tokens
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg['token_endpoint']

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Find and check the URL that gives user's profile info
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # If user email is verified by Google, get user's info
    if userinfo_response.json().get('email_verified'):
        userinfo_response_json = userinfo_response.json()
        user_unique_id = userinfo_response_json['sub']
        user_email = userinfo_response_json['email']
        user_picture = userinfo_response_json['picture']
        user_name = userinfo_response_json['given_name']
    else:
        abort(
            400,
            description='User email not available or not verified by Google')

    # Create the user in db if needed then log it
    if storage.get(User, user_unique_id) is None:
        user = User(id=user_unique_id, email=user_email,
                    profile_pic=user_picture, name=user_name)
        storage.new(user)
        storage.save()

    login_user(user)
    return jsonify({'User successfully authenticated'}), 200


@app_views.route('/logout')
@login_required
def logout():
    """Logout the user"""
    logout_user()
    return jsonify({'User successfully disconnected'}), 200
