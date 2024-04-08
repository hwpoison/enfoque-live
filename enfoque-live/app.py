from flask import Flask, Blueprint, Response, request, render_template, \
    redirect, url_for, send_file, session, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import configuration

from mercadopago_checkout import mp_checkout
from stream import stream as stream_route
from admin import admin as admin_route
import auth

import database
import log


CONFIGURATION_FILENAME = "app_settings.json"

app = Flask(__name__)
jwt = JWTManager(app)
CORS(app)

app.register_blueprint(mp_checkout)
app.register_blueprint(auth.auth)
app.register_blueprint(stream_route)
app.register_blueprint(admin_route)

# init db
database.create_table()

app.config.update(configuration.get_vars())

# init logging handler and lvl
app.logger.setLevel(log.logging.INFO)
app.logger.addHandler(log.handler)
app.logger.info("EnfoqueLive v1.0 started.")

#set up jwt
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["SESSION_COOKIE_DOMAIN"] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SECURE'] = False

# Set ersistent jwt for fronted side for when browser is restarted
app.config['JWT_SESSION_COOKIE'] = False 

app.config["WTF_CSRF_CHECK_DEFAULT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 172800
app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]


@app.route('/')
def index():
    auth.verify_jwt_in_request(optional=True)
    current = auth.get_jwt_identity()
    if current == "admin":
        return redirect(url_for("admin.panel"))
    else:
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
