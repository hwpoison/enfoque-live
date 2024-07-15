from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, current_app
from utils import configuration, auth, tokens
from utils.upload import upload_file
from utils.tokens import generate_image_id
from utils import server_status
from models import viewers
from models import tokens as tokens_db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/monitor')
@auth.is_auth("admin")
def monitor():
    return render_template('admin/monitor_stream.html', stream_name=configuration.get("hls_key"))

@admin.route('/panel')
@auth.is_auth("admin")
def panel():
    """
    Administration panel with stats
    """
    all_sold_tokens = tokens_db.count_all_sold_tokens()

    total_current_viewers = viewers.get_current_viewers()
    return render_template('admin/panel.html',
            misc={'all_sold_tokens': all_sold_tokens,
                  'total_current_viewers': viewers.get_current_viewers_without_lock()
            },
            pconfig=configuration.get_vars())


@admin.route('/links')
@auth.is_auth("admin")
def link_manager():
    """
    View to manage the links
    """
    return render_template('admin/link_manager.html',
                           action_msg=request.args.get("action_msg"),
                           data=tokens_db.retrieve_tokens(),
                           pconfig=configuration.get_vars())

@admin.route('/configuration')
@auth.is_auth("admin")
def configurations():
    """
    View to manage the stream configurations
    """
    return render_template('admin/configuration.html',
                           pconfig=configuration.get_vars())

@admin.route('/config/update', methods=['POST'])
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
                return jsonify({"error": "Invalid image"}), 400

        # Update configuration with new values
        for key, value in request.form.items():
            section, field = key.split('.')
            configuration.set(field, value, sec=section)

        current_app.logger.info("Configuration updated.")
        return jsonify({"message": "Configuration updated"}), 200
    except Exception as e:
        current_app.logger.error("Error updating configuration: %s", e)
        return jsonify({"error": "Error updating configuration"}), 500
