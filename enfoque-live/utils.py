import secrets
import random
import database


def generate_token(alias=False, status=""):
    if not alias:
        alias = str(random.randint(100, 99999))
    token = secrets.token_urlsafe(16)
    database.store_token(token, alias, None, status, False)
    return token