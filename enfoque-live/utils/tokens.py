import secrets
import random

def generate_token():
    token = secrets.token_urlsafe(16)
    return token

def generate_alias():
    return str(random.randint(100, 99999))

def generate_error_id():
    return secrets.token_urlsafe(8)

def generate_image_id():
    return secrets.token_urlsafe(5)