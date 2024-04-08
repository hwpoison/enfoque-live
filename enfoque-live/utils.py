import secrets
import random
import database


def generate_token(alias=False):
    if not alias:
        alias = str(random.randint(100, 99999))
    token = secrets.token_urlsafe(16)
    database.store_token(token, alias, None, "created by admin", False)
    return token


def generate_candidate_token():
    alias = str(random.randint(100, 99999))
    token = secrets.token_urlsafe(16)
    database.store_token(token, alias, None, "to_approve", False)
    return token
