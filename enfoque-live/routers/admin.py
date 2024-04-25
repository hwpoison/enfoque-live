from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, current_app
from utils import configuration, auth, tokens
from utils.upload import upload_file
from utils.tokens import generate_image_id

from models import tokens as tokens_db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/monitor')
@auth.is_admin()
def monitor():
    return render_template('admin/monitor_stream.html', stream_name=configuration.get("hls_key"))

@admin.route('/panel')
@auth.is_admin()
def panel():
    return render_template('admin/panel.html',
                           action_msg=request.args.get("action_msg"),
                           data=tokens_db.retrieve_tokens(),
                           pconfig=configuration.get_vars()['DEFAULT'])

@admin.route('/token_action', methods=['POST'])
@auth.is_admin()
def token_action():
    alias = request.form['alias']
    action = request.form['select_action']
    msg = None
    anchor = "actions-section"
    try:
        if action == "create":
            if not alias:
                alias = tokens.generate_alias()
            token = tokens_db.create_token(token_value=tokens.generate_token(), name=alias, status="created_by_admin")
            current_app.logger.info(
                f"[{ alias }][{ token }] has been created.")
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
        msg = "Error"
        current_app.logger.error(
            f"Error during 'token_action' action: {error}")

    return redirect(url_for("admin.panel", action_msg=msg, _anchor=anchor))


@admin.route('/ban_token', methods=['POST'])
@auth.is_admin()
def ban_token():
    token = request.form['token']
    tokens_db.ban_token(token)
    return redirect(url_for('admin.panel', _anchor=token))


@admin.route('/unhold_token', methods=['POST'])
@auth.is_admin()
def unhold_token():
    token = request.form['token']
    tokens_db.update_token_footprint(token, None)
    current_app.logger.info(f"[{ token }] token has been unholded.")
    return redirect(url_for('admin.panel', _anchor=token))


@admin.route('/update_config', methods=['POST'])
@auth.is_admin()
def update_config():
    generic_data = request.form.to_dict()

    if poster_image:=request.files.get("player_poster_image"):
        cover_name = f"poster_{generate_image_id()}"
        upload = upload_file(poster_image, target_name=cover_name)
        if upload:
            generic_data['player_poster_image'] = "/" + upload
        else:
            print("invalid image")

    for key, new_val in generic_data.items():
        configuration.set(key, new_val)

    current_app.logger.info("Configuration updated.")
    return 'configuration updated', 200
