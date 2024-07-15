from models.database import db, Token
from datetime import datetime
from math import ceil

def ban_token(token_value):
    token = Token.query.filter_by(token=token_value).first()
    if token:
        if token.banned:
            token.banned = False
            db.session.commit()
            return {"message": "Token unbanned successfully"}
        else:
            token.banned = True
            db.session.commit()
            return {"message": "Token banned successfully"}
    else:
        return {"message": "Token not found"}

def get(token_value):
    return Token.query.filter_by(token=token_value).first()

def delete_token_by_alias(token_name):
    token = Token.query.filter_by(name=token_name).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        return {"message": "Token deleted successfully"}
    else:
        return {"message": "Token not found"}

def delete_token(token):
    token = Token.query.filter_by(token=token).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        return {"message": "Token deleted successfully"}
    else:
        return {"message": "Token not found"}

def delete_all_tokens():
    Token.query.delete()
    db.session.commit()

def update_token_footprint(token_value, new_footprint):
    token = Token.query.filter_by(token=token_value).first()
    if token:
        token.footprint = new_footprint
        db.session.commit()
        return {"message": "Token footprint updated successfully"}
    else:
        return {"message": "Token not found"}

def search_token(query, page=1, per_page=300): # TODO: pagination with search elements on frontend
    try:
        tokens_query = Token.query.filter((Token.name.ilike(f'%{query}%')) | (Token.token.ilike(f'%{query}%'))).paginate(page=page, per_page=per_page)
        tokens = tokens_query.items
        total_pages = ceil(tokens_query.total / per_page)
        all_tokens = {}
        for token in tokens:
            all_tokens[token.id] = {
                "name": token.name,
                "token": token.token,
                "footprint": token.footprint,
                "status": token.status,
                "sold": token.sold,
                "banned": token.banned,
                "created_at": token.created_at
            }
        return all_tokens, total_pages
    except:
        return {},0

def retrieve_tokens():
    tokens = Token.query.filter(Token.status != None).all()
    token_info = {}
    for token in tokens:
        token_info[token.id] = {
            "name": token.name,
            "token":token.token,
            "footprint": token.footprint,
            "status": token.status,
            "sold": token.sold,
            "banned": token.banned,
            "created_at": token.created_at
        }
    return  token_info

def retrieve_tokens_paginate(page=1, per_page=30):
    """
    Retrieve tokens with pagination
    """
    try:
        tokens_query = Token.query.filter(Token.status != None).paginate(page=page, per_page=per_page)
        tokens = tokens_query.items
        total_pages = ceil(tokens_query.total / per_page)
        all_tokens = {}
        for token in tokens:
            all_tokens[token.id] = {
                "name": token.name,
                "token": token.token,
                "footprint": token.footprint,
                "status": token.status,
                "sold": token.sold,
                "banned": token.banned,
                "created_at": token.created_at
            }
        return all_tokens, total_pages
    except:
        return {},0

def check_token_existence(token_value):
    token = Token.query.filter_by(token=token_value).first()
    if token:
        return True
    else:
        return False

def create_token(token_value=None, name=None, footprint=None, status=None, sold=False, banned=False):
    new_token = Token(token=token_value, 
                      name=name, 
                      footprint=footprint, 
                      status=status, 
                      sold=sold, 
                      banned=banned
    )
    db.session.add(new_token)
    db.session.commit()
    print(f'Token {token_value} creado exitosamente.')

def count_all_sold_tokens():
    return Token.query.filter(Token.sold == True).count()

def save():
    db.session.commit()