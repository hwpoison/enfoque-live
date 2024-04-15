from flask import Flask, Blueprint, Response, request, render_template, \
    redirect, url_for, send_file, session, jsonify, make_response

from flask_cors import CORS


from utils.cache import cache 

from flask_jwt_extended import JWTManager

from utils import configuration

from routers.buy import mp_checkout as mp_route
from routers.stream import stream as stream_route
from routers.admin import admin as admin_route
from routers.auth import auth as auth_route

import database
from utils import log, auth
from utils.compression import compress_response

app = Flask(__name__)
jwt = JWTManager(app)
CORS(app)


app.register_blueprint(mp_route)
app.register_blueprint(auth_route)
app.register_blueprint(stream_route)
app.register_blueprint(admin_route)

# init db
database.create_table()

# load configuration file
app.config.update(configuration.get_vars())

# init logging handler and lvl
app.logger.setLevel(log.logging.INFO)
app.logger.addHandler(log.handler)
app.logger.info("EnfoqueLive v1.0 started.")

#set up jwt
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["SESSION_COOKIE_DOMAIN"] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SECURE'] = True

# Set ersistent jwt for fronted side for when browser is restarted
app.config['JWT_SESSION_COOKIE'] = False 

app.config["WTF_CSRF_CHECK_DEFAULT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 172800
app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]

# set response compressions
app.after_request(compress_response)

@app.route('/')
def index():
    auth.verify_jwt_in_request(optional=True)
    identity = auth.get_identity()
    if identity:
        if identity['role'] == "admin":
            return redirect("/panel")
    return redirect("/comprar")

@app.route('/update_config', methods=['POST'])
def update_config():
    app.logger.info("Configuration updated.")
    generic_data = request.form.to_dict()
    app.config.update(generic_data)

    for key in list(configuration.get_vars()):
        configuration.set(key, app.config.get(key))
    return '', 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)