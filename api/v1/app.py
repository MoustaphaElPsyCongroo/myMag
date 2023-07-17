#!/usr/bin/python3
"""Flask Application"""
import logging
import os
from datetime import datetime
from decouple import config
from models import storage
from api.v1.views import app_views
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
from flasgger import Swagger
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
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

job_defaults = {
    'misfire_grace_time': None,
    'coalesce': True,
    'max_instances': 3
}
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)
logging.getLogger(
    'api.v1.cronjobs.update_article_scores').setLevel(logging.INFO)
logging.getLogger(
    'api.v1.utils.user_articles').setLevel(logging.INFO)

scheduler = BackgroundScheduler(job_defaults=job_defaults)
scheduler.add_job(cronjobs.get_random_header_list, 'cron', day=1, hour=0)
scheduler.add_job(cronjobs.fetch_new_articles, 'interval',
                  minutes=10, next_run_time=datetime.now())
scheduler.add_job(cronjobs.update_article_scores, 'interval', minutes=10)
scheduler.add_job(cronjobs.extract_weekly_stats, 'cron', hour=0)
scheduler.add_job(cronjobs.populate_tags, 'cron',
                  hour=5, next_run_time=datetime.now())
scheduler.start()


@app.teardown_appcontext
def close_db(error):
    """Close Storage"""
    storage.close()


@app.errorhandler(HTTPException)
def handle_http_exceptions(e):
    """ Jsonify HTTP exceptions"""
    return jsonify(error=str(e)), e.code


app.config['SWAGGER'] = {
    'title': 'myMag RESTful API',
    'uiversion': 3
}

# TODO: Add Swagger compatibility and documentation for all routes
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
