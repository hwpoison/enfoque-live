from flask import Blueprint, jsonify, request, current_app, redirect, url_for, current_app
from utils import auth, tokens
from models import tokens as tokens_db

token = Blueprint('tokens', __name__, url_prefix='/tokens')


@token.route('/all/page/<int:page>', methods=['GET'])
@auth.is_auth("admin")
def retrieve_tokens_pagination(page : int):
    """
    API to retrieve tokens
    """
    all_tokens, total_pages = tokens_db.retrieve_tokens_paginate(page=page)
    print(all_tokens)
    if page > total_pages:
        print("page limit!!")
        return jsonify({'message':"no more"}), 500

    print("final")
    return jsonify({'tokens': all_tokens,
                    'total_pages': total_pages})


@token.route('/all', methods=['GET'])
@auth.is_auth("admin")
def retrieve_tokens():
    """
    API to retrieve tokens
    """
    return jsonify({'tokens': tokens_db.retrieve_tokens()})

@token.route('delete', methods=['DELETE'])
@auth.is_auth("admin")
def delete_token_deprecate():
    try:
        data = request.get_json()
        token = data.get('token')
        tokens_db.delete_token(token)
        return jsonify({'message': f'Token {token} deleted successfully'}), 200
    except Exception as error:
        current_app.logger.error(f"Error during 'delete_token' action: {error}")
        return jsonify({'message': 'Error deleting token'}), 500


@token.route('ban', methods=['POST'])
@auth.is_auth("admin")
def ban_token():
    """
     Ban a stream token
    """
    try:
        data = request.get_json()
        token = data.get('token')
        msg = tokens_db.ban_token(token)
        return jsonify(msg), 200
    except Exception as error:
        current_app.logger.error(f"Error during 'ban_token' action: {error}")
        return jsonify({'message': 'Error banning token'}), 500


@token.route('unhold', methods=['POST'])
@auth.is_auth("admin")
def unhold_token():
    """
    Unhold a stream token
    """
    data = request.get_json()
    token = data.get('token')
    if token:
        tokens_db.update_token_footprint(token, None)
        current_app.logger.info(f"[{token}] token has been unholded.")
        return jsonify({'message':'Token unholded correctly'}),200
    else:
        current_app.logger.error("Token not provided")
        return jsonify({'message':'Token not provided'}), 400

@token.route('/create', methods=['POST'])
@auth.is_auth("admin")
def create_token():
    alias = request.form.get('alias')
    try:
        if not alias:
            alias = tokens.generate_alias()
        token_value = tokens.generate_token()
        token = tokens_db.create_token(token_value=token_value, name=alias, status="created_by_admin")
        current_app.logger.info(f"[{alias}][{token}] has been created.")
        return jsonify({"message": "Token created"}), 200
    except Exception as error:
        current_app.logger.error(f"Error during 'create_token' action: {error}")
        return jsonify({"message": "Error during token creation"}), 500

@token.route('/delete', methods=['POST'])
@auth.is_auth("admin")
def delete_token():
    alias = request.form.get('alias')
    try:
        tokens_db.delete_token_by_alias(alias)
        current_app.logger.info(f"Token '{alias}' has been deleted.")
        return jsonify({"message": f"'{alias}' deleted"}), 200
    except Exception as error:
        current_app.logger.error(f"Error during 'delete_token' action: {error}")
        return jsonify({"message": "Error during token deletion"}), 500

@token.route('/delete_all', methods=['POST'])
@auth.is_auth("admin")
def delete_all_tokens():
    try:
        tokens_db.delete_all_tokens()
        current_app.logger.info("All tokens have been deleted.")
        return jsonify({"message": "All tokens deleted"}), 200
    except Exception as error:
        current_app.logger.error(f"Error during 'delete_all_tokens' action: {error}")
        return jsonify({"message": "Error during deletion of all tokens"}), 500

@token.route('/search/<query>', methods=['GET'])
@auth.is_auth("admin")
def search_token(query):
    try:
        all_tokens, total_pages = tokens_db.search_token(query)

        return jsonify({'tokens': all_tokens,
                        'total_pages': total_pages})

    except Exception as error:
        current_app.logger.error(f"Error during 'search_token' action: {error}")
        return jsonify({"message": "Error during token search"}), 500
