# #!/usr/bin/python3
# """Google Auth"""
# from decouple import config
# from app import app
# import requests
# from models import storage
# from models.user import User
# from flask import abort, jsonify, redirect, request, session
# import google
# from google.oauth2 import id_token
# from google_auth_oauthlib.flow import Flow
# import json
# import jwt
# from oauthlib.oauth2 import WebApplicationClient
# import os
# import pathlib

# GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
# client_secrets_file = os.path.join(
#     pathlib.Path(__file__).parent, 'client-secret.json')
# algorithm = config('JWT_ENCODE_ALGORITHM')
# BACKEND_URL = config('BACKEND_URL')
# FRONTEND_URL = config('FRONTEND_URL')

# # Bypass http warnings ---- IN TESTING ONLY, NEVER IN PRODUCTION ---
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# """Find what URL to redirect to for Google login
#     and what user information to retrieve
# """
# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=['profile', 'email', 'openid'],
#     redirect_uri=f'{BACKEND_URL}/login/callback'
# )


# def login_required(function):
#     def wrapper(*args, **kwargs):
#         """Decorator for auth validation, in the example of Flask-Login"""
#         encoded_jwt = request.headers.get('Authorization').split('Bearer ')[1]
#         if encoded_jwt is None:
#             return abort(401)
#         else:
#             return function()
#     return wrapper


# def Generate_JWT(payload):
#     """Generate a JSON Web Token"""
#     encoded_jwt = jwt.encode(payload, app.secret_key, algorithm=algorithm)
#     return encoded_jwt


# @app.route('login/callback')
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
#         audience=GOOGLE_CLIENT_ID
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
#     return redirect(f'{FRONTEND_URL}?jwt={jwt_token}')
#     # return jsonify({'JWT': jwt_token}), 200


# @app.route('/auth/google')
# def login():
#     """Get Google's authorization url and store the state so that
#     the callback can verify the auth server response
#     """
#     authorization_url, state = flow.authorization_url()
#     session['state'] = state
#     return jsonify({'auth_url': authorization_url}), 200


# @app.route('/logout')
# def logout():
#     """Clear user's id from the flask session
#     """
#     # Don't forget to clear the localStorage from the frontend
#     session.clear()
#     return jsonify({'message': 'User successfully logged out'}), 202


# # A remplacer par la route User quand on la fera puis suppirmer celle la,
# # c'est juste pour tester
# # Euh, quoique… A voir quand j'aurai testé depuis React
# @app.route('/home')
# @login_required
# def home_page_user():
#     encoded_jwt = request.headers.get('Authorization').split('Bearer')[1]
#     try:
#         decoded_jwt = jwt.decode(
#             encoded_jwt, app.secret_key, algorithm=algorithm)
#         # print(decoded_jwt)
#     except Exception as e:
#         return jsonify({
#             'message': 'Decoding JWT failed',
#             'exception': e.args
#         }), 500
#     return jsonify({
#         'Decoded JWT': decoded_jwt
#     }), 200
