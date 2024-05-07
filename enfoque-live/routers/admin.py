from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, current_app
from utils import configuration, auth, tokens
from utils.upload import upload_file
from utils.tokens import generate_image_id

from models import tokens as tokens_db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/monitor')
@auth.is_auth("admin")
def monitor():
    return render_template('admin/monitor_stream.html', stream_name=configuration.get("hls_key"))


@admin.route('/panel')
@auth.is_auth("admin")
def panel():
    return render_template('admin/panel.html',
                           action_msg=request.args.get("action_msg"),
                           data=tokens_db.retrieve_tokens(),
                           pconfig=configuration.get_vars()['DEFAULT'])


@admin.route('/token_action', methods=['POST'])
@auth.is_auth("admin")
def token_action():
    """
    Handle token actions (create, delete, delete all)
    """
    alias = request.form.get('alias')
    action = request.form.get('select_action')
    msg = None
    anchor = "actions-section"

    try:
        if action == "create":
            if not alias:
                alias = tokens.generate_alias()
            token = tokens_db.create_token(token_value=tokens.generate_token(), name=alias, status="created_by_admin")
            current_app.logger.info(f"[{alias}][{token}] has been created.")
            msg = f"'Enlace {alias}' creado"
            anchor = "end-of-page"
        elif action == "delete":
            tokens_db.delete_token_by_alias(alias)
            msg = f"'{alias}' eliminado"
        elif action == "delete_all":
            tokens_db.delete_all_tokens()
            msg = f"Todos los enlaces han sido eliminados"
        else:
            msg = "Acción desconocida"
    except Exception as error:
        msg = "Error al ejecutar la acción"
        current_app.logger.error(f"Error during 'token_action' action: {error}")

    return redirect(url_for("admin.panel", action_msg=msg, _anchor=anchor))


@admin.route('/ban_token', methods=['POST'])
@auth.is_auth("admin")
def ban_token():
    """
     Ban a stream token
    """
    token = request.form.get('token')
    if token:
        tokens_db.ban_token(token)
        current_app.logger.info(f"[{token}] token has been banned.")
        return redirect(url_for('admin.panel', _anchor=token))
    else:
        current_app.logger.error("Token not provided")
        return "Error: Token not provided", 400

@admin.route('/unhold_token', methods=['POST'])
@auth.is_auth("admin")
def unhold_token():
    """
    Unhold a stream token
    """
    token = request.form.get('token')
    if token:
        tokens_db.update_token_footprint(token, None)
        current_app.logger.info(f"[{token}] token has been unholded.")
        return redirect(url_for('admin.panel', _anchor=token))
    else:
        current_app.logger.error("Token not provided")
        return "Error: Token not provided", 400


@admin.route('/update_config', methods=['POST'])
@auth.is_auth("admin")
def update_config():
    """
    Update configuration file with new values
    """
    try:
        generic_data = request.form.to_dict()

        # Handle poster image upload
        poster_image = request.files.get("player_poster_image")
        if poster_image:
            cover_name = f"poster_{generate_image_id()}"
            upload = upload_file(poster_image, target_name=cover_name)
            if upload:
                generic_data['player_poster_image'] = "/" + upload
            else:
                print("Invalid image")

        # Update configuration with new values
        for key, new_val in generic_data.items():
            configuration.set(key, new_val)

        current_app.logger.info("Configuration updated.")
        return 'Configuration updated', 200
    except Exception as e:
        current_app.logger.error("Error updating configuration: %s", e)
        return 'Error updating configuration', 500
