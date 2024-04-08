from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, set_refresh_cookies, create_refresh_token, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity, get_jwt, unset_jwt_cookies
from flask_jwt_extended import jwt_required, jwt_manager

from functools import wraps

admin_users = {
    'master': 'nfoq2024$',
    'sergio': 'danielito52',
}


auth = Blueprint('auth', __name__)

def is_admin():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request(optional=True)
            current_user = get_jwt_identity()
            if current_user == "admin":
                return fn(*args, **kwargs)
            else:
                return redirect("/")
        return decorator
    return wrapper


def get_identity():
    return get_jwt_identity()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        if user in admin_users and admin_users[user] == password:
            access_token = create_access_token(identity="admin")
            resp = make_response(redirect('/panel', 302))
            set_access_cookies(resp, access_token)
            return resp
        else:
            return render_template("admin/login_fail.html")
    else:
        return render_template('admin/login.html')


@auth.route('/logout')
def logout():
    resp = make_response(redirect('/login', 302))
    unset_jwt_cookies(resp)
    return resp
