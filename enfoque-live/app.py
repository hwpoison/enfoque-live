import os
import datetime

import redis
from flask import Flask, request, redirect, url_for, send_file, make_response, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from jwt.exceptions import ExpiredSignatureError

from utils import configuration
from utils.limiter import limiter

from routers.stream import stream as stream_route
from routers.buy import mp_checkout as mp_route
from routers.admin import admin as admin_route
from routers.auth import auth as auth_route
from routers.home import home as home_route
from routers.tokens import token as tokens_route

from utils.compression import compress_response
from utils import log, auth

from models.database import db

# Configuration
PRODUCTION_DB = "sqlite:///database.db"
TEST_DB = "sqlite:///test_database.db"

def create_app(testing=False):
    app = Flask(__name__)
    jwt = JWTManager(app)
    CORS(app)

    # set up blueprints
    app.register_blueprint(mp_route)
    app.register_blueprint(auth_route)
    app.register_blueprint(stream_route)
    app.register_blueprint(admin_route)
    app.register_blueprint(home_route)
    app.register_blueprint(tokens_route)

    # init logging handler and lvl
    app.logger.setLevel(log.logging.INFO)
    app.logger.addHandler(log.handler)

    app.logger.info("EnfoqueFutbol v2.0 started.")

    # Setup JWT
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config["SESSION_COOKIE_DOMAIN"] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_COOKIE_SECURE'] = True if configuration.get(
        "in_production") == True else False

    # Set persistent jwt for fronted side for when browser is restarted
    app.config['JWT_SESSION_COOKIE'] = False

    app.config["WTF_CSRF_CHECK_DEFAULT"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=3)
    app.config["JWT_SECRET_KEY"] = configuration.get("secret_key")

    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    app.jinja_options["trim_blocks"] = True

    # Compression middleware ( Handled by nginx )
    # app.after_request(compress_response)

    # Rate limiter 
    limiter.init_app(app)

    # Database configuration
    db_uri = TEST_DB if testing else PRODUCTION_DB
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    db.init_app(app) 

    # Setup REDIS
    with app.app_context():
        app.config['REDIS_CLIENT'] = redis.StrictRedis(
            host='127.0.0.1', port=6379, db=0
    )

    @app.route('/')
    def index():
        auth.verify_jwt_in_request(optional=True)
        identity = auth.get_identity()
        if identity:
            if identity['role'] == "admin":
                return redirect(url_for("admin.panel"))
        return redirect(url_for("mp_checkout.buy"))
    
    # If the JWT token is expired, unset it and redirect
    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token_error(error):
        """
            TODO: IMPLEMENT A REFRESH
        """
        response = make_response(redirect(request.url))
        auth.unset_identity(response)
        return response

    #@app.errorhandler(404) 
    #def not_found(e): 
    #    return redirect("/")

    return app

app = create_app()

# Drop and recreate all db
recreate_db = False
if recreate_db or os.path.exists("instance/database.db") == False:
    with app.app_context():
        db.drop_all()
        db.create_all()


# Force HTTPS behind the proxy
from werkzeug.middleware.proxy_fix import ProxyFix
if configuration.get("in_production"):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
