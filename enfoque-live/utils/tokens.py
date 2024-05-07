import secrets
import random

def generate_token() -> str:
    """
    Generate a URL-safe token using secrets module
    This token will be used to identify a stream
    """
    token = secrets.token_urlsafe(16)
    return token

def generate_alias() -> str:
    """
    Generate a random alias between 100 and 99999
    This alias will be used to identify a stream
    """
    return str(random.randint(100, 99999))

def generate_error_id() -> str:
    """
    Generate a short error ID using secrets module
    This ID will be used to identify an error
    """
    return secrets.token_urlsafe(8)

def generate_image_id() -> str:
    """
    Generate a short image ID using secrets module
    This ID will be used to identify an image
    """
    return secrets.token_urlsafe(5)