from flask import Blueprint, render_template, request, current_app, redirect, make_response
from utils.auth import * 
from utils import configuration
import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')

        admin_user = configuration.get("admin_user") 
        admin_password = configuration.get("admin_password")

        if user == admin_user and password == admin_password:
            expires = datetime.timedelta(days=365)
            access_token = create_access_token(identity={'role':'admin'}, expires_delta=expires)
            resp = make_response(redirect('/admin/panel', 302))
            set_access_cookies(resp, access_token)
            return resp
        else:
            current_app.logger.error(f"administrator login fail using { user } { password } from { request.remote_addr }")
            return render_template("admin/login_fail.html"), 401
    else:
        return render_template('admin/login.html')


@auth.route('/logout')
def logout():
    resp = make_response(redirect('/login', 302))
    unset_identity(resp)
    return resp