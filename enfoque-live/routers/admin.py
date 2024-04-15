from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, current_app
from utils import configuration, auth, tokens
import database


admin = Blueprint('admin', __name__)

@admin.route('/monitor')
@auth.is_admin()
def monitor():
    return render_template('admin/monitor_stream.html', stream_name=configuration.get("HLS_KEY"))

@admin.route('/panel')
@auth.is_admin()
def panel():
    return render_template('admin/panel.html',
                           action_msg=request.args.get("action_msg"),
                           data=database.retrieve_tokens(),
                           pconfig=configuration.get_vars())

@admin.route('/token_action', methods=['POST'])
@auth.is_admin()
def generate_url():
    alias = request.form['alias']
    action = request.form['select_action']
    msg = ""
    try:
        if action == "create":
            token = tokens.generate_token(alias=alias, status="created_by_admin")
            current_app.logger.info(
                f"[{ alias }][{ token }] has been created.")
            msg = f"'Enlace {alias}' creado"

        elif action == "delete":
            database.delete_token_by_alias(alias)
            msg = f"{alias}' eliminado"

        elif action == "delete_all":
            database.delete_all_tokens()
            msg = f"Todos los enlaces han sido eliminados. Si te equivocaste y querés recuperarlos, usá la opción restaurar desde backup"
        
        elif action == "restore_from_backup":
            database.restore_tokens_from_backup()
            msg = f"Enlaces restaurados"
        
        else:
            msg = "Acción desconocida"
    except Exception as error:
        msg = "Error"
        current_app.logger.error(
            f"Error during 'token_action' action: {error}")

    return redirect(url_for("admin.panel", action_msg=msg))


@admin.route('/delete_token', methods=['POST'])
@auth.is_admin()
def delete_token():
    token = request.form['token']
    database.delete_token_(token)
    current_app.logger.info(f"[{ token }] token has been banned.")
    return redirect(url_for('admin.panel'))


@admin.route('/unhold_token', methods=['POST'])
@auth.is_admin()
def unhold_token():
    token = request.form['token']
    database.set_footprint(token, None)
    current_app.logger.info(f"[{ token }] token has been unholded.")
    return redirect(url_for('admin.panel'))
