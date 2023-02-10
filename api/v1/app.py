#!/usr/bin/python3
"""Flask Application"""
from decouple import config
from models import storage
from models.user import User
from api.v1.views import app_views
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_router import Google, JwtRoutes
from flasgger import Swagger

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.url_map.strict_slashes = False
app.register_blueprint(app_views)
app.secret_key = config('SECRET_KEY')
cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})


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


if __name__ == "__main__":
    """Main Function"""
    host = config('MYMAG_API_HOST')
    port = config('MYMAG_API_PORT')
    if not host:
        host = '0.0.0.0'
    if not port:
        port = '5000'
    app.run(host=host, port=port, threaded=True)
