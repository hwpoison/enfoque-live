from flask import redirect

from flask_jwt_extended import create_access_token, set_access_cookies, set_refresh_cookies, create_refresh_token, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity, get_jwt, unset_jwt_cookies
from flask_jwt_extended import jwt_required, jwt_manager

from functools import wraps

def is_auth(*allowed_roles):
    """
    Authentication decorator to check if request has allowed role.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = get_identity()
            if identity and (current_role:=identity.get('role')):
                if current_role in allowed_roles:
                    return fn(*args, **kwargs)
            return redirect("/")
        return wrapper
    return decorator

def get_identity():
    """
    Get current JWT identity
    """
    verify_jwt_in_request(optional=True)
    return get_jwt_identity()

def unset_identity(resp):
    """
    Unset current JWT token from client
    """
    unset_jwt_cookies(resp)