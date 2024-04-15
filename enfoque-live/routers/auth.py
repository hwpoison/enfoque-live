from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, make_response
from utils.auth import * 

from functools import wraps

admin_users = {
    'admin':'admin993881'
}

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        if user in admin_users and admin_users[user] == password:
            identity = {'role':'admin'}
            access_token = create_access_token(identity=identity)
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
    unset_identity(resp)
    return resp