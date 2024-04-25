from flask import redirect

from flask_jwt_extended import create_access_token, set_access_cookies, set_refresh_cookies, create_refresh_token, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity, get_jwt, unset_jwt_cookies
from flask_jwt_extended import jwt_required, jwt_manager

from functools import wraps

def is_admin():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                if identity['role'] == "admin":
                    return fn(*args, **kwargs)
            return redirect("/")
        return decorator
    return wrapper

def is_auth():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                    return fn(*args, **kwargs)
            return redirect("/")
        return decorator
    return wrapper

def get_identity():
    verify_jwt_in_request(optional=True)
    return get_jwt_identity()

def unset_identity(resp):
    unset_jwt_cookies(resp)