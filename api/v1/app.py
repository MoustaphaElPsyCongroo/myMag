#!/usr/bin/python3
"""Flask Application"""
import os
from decouple import config
from models import storage
from api.v1.views import app_views
from flask_cors import CORS
from flasgger import Swagger
from flask import Flask, jsonify
import api.v1.cronjobs as cronjobs


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
app.secret_key = os.urandom(24)
google_credentials = config('GOOGLE_CREDENTIALS')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials
cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
CORS(app)

print(cronjobs.fetch_new_articles())


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


# Bypass http warnings ---- IN TESTING ONLY, NEVER IN PRODUCTION ---
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


if __name__ == "__main__":
    """Main Function"""
    host = config('MYMAG_API_HOST')
    port = config('MYMAG_API_PORT')
    if not host:
        host = '0.0.0.0'
    if not port:
        port = '5000'
    app.run(host=host, port=port, threaded=True)
