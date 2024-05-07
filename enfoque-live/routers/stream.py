from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, current_app, make_response

import hashlib
import os
from utils import auth, tokens
from utils import configuration
from utils import stream_dispatcher 
from models import tokens as tokens_db

from utils.limiter import limiter
stream = Blueprint('stream', __name__)

@stream.route('/monitoring')
@stream.route('/monitoring/<chunk_name>')
@auth.is_auth("admin")
def monitorig(chunk_name=None):
    return stream_dispatcher.send_chunk(chunk_name)


@stream.route('/get/<chunk_name>')
def stream_playlist(chunk_name=None):
    return stream_dispatcher.send_chunk(chunk_name)


@stream.route('/status/<stream_token>')
@limiter.limit("4 per 10 seconds")
@auth.is_auth('admin', 'client')
def stream_status(stream_token: str):
    """
    Handles stream status info
    :param stream_token: The stream token

    """
    try:
        # register/refresh the view
        redis_client = current_app.config['REDIS_CLIENT']
        redis_client.setex(f"active_user:{stream_token}", 10, 'active')
        playlist_location = f"{configuration.get('hls_dir')}{configuration.get('hls_key')}"

        # count total viewers but only each 10 secs to avoid a bunch of simultaneous scan_iter
        if not redis_client.exists("viewers_count_lock"):
            viewers = 0
            for _ in redis_client.scan_iter('active_user*'):
                viewers+=1
            redis_client.set("total_current_viewers", viewers)
            redis_client.setex("viewers_count_lock", 10, 1)

        total_current_viewers = int(redis_client.get("total_current_viewers") or 0)

        status_info = {
            "event_info":{
                'stream_title': configuration.get('stream_title'), 
                "stream_date_info": configuration.get('stream_date_info'),
                "stream_subtitle": configuration.get('stream_subtitule'),
                "player_poster_image": configuration.get('player_poster_image'),
                'current_viewers': total_current_viewers
            }
        }

        if os.path.exists(playlist_location):
            status_info['status'] = "online"
        else:
            status_info['status'] = "offline"

        return jsonify(status_info), 200
    except Exception as e:
            current_app.logger.error(f"Error getting stream status: {e}")
            return jsonify({"error": "Failed to get stream status"}), 500


@stream.route('/play/<stream_token>')
@stream.route('/play/<stream_token>/<chunk_name>')
def play(stream_token, chunk_name=None):
    """
    Handles playback requests for a given stream token.

    :param stream_token: The token identifying the stream to play
    :param chunk_name: The name of the chunk to play (optional)
    :return: A response object redirecting to the stream or an error page
    """
    play_id = tokens.generate_error_id()
    hls_key = configuration.get("hls_key")

    # Generate the request footprint
    remote_ip_address = request.remote_addr
    hash_string = f"{remote_ip_address}{stream_token}"
    footprint = hashlib.md5(hash_string.encode()).hexdigest()

    # Check if request has a identity
    auth.verify_jwt_in_request(optional=True)
    current_identity = auth.get_identity()

    # if not assign one
    if current_identity == None:
        current_app.logger.info(f"[{play_id}] Doens't have identity, assigning one: {footprint}")
        identity = {'role':'client', 'footprint':footprint}
        expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        access_token = auth.create_access_token(identity=identity, expires_delta=expires)
        send_jwt = make_response(redirect(url_for("stream.play", stream_token=stream_token)))
        auth.set_access_cookies(send_jwt, access_token)
        return send_jwt

    current_app.logger.info(f"[{play_id}] Incoming connection from '{ remote_ip_address }' with '{ current_identity }' identity")

    # current request identity
    identity_role = current_identity.get('role')
    identity_footprint = current_identity.get('footprint')

    # get requested token info
    token_data = tokens_db.get(stream_token)

    # handle errors
    if token_data is None:
        current_app.logger.error(f"[{play_id}] The token '{stream_token}' doens't exists")
        return render_template('generic_advertence.html', 
                                error_id=play_id,
                                title="Error", 
                                message="Este enlace no es valido o ha sido eliminado. ⛓️‍💥"), 404
    elif token_data.banned:
            return render_template('generic_advertence.html', 
                                    title="Error", 
                                    message="Este enlace ha sido deshabilitado. ⛓️‍💥"), 404

    # if the token is not claimed, claim it
    if token_data.footprint is None and current_identity.get('role') != 'admin':
        token_data.footprint = identity_footprint
        tokens_db.save()
        current_app.logger.info(f"[{play_id}] [{ remote_ip_address }]  { current_identity } claimed '{ stream_token }' stream.")

    # starts the verification
    if token_data.footprint == identity_footprint \
        or token_data.footprint == footprint \
            or identity_role == "admin" \
                or configuration.get('free_mode') == 'enabled':
        if chunk_name:
            return stream_dispatcher.send_chunk(chunk_name)
        else:  # Serve the main view / playlist
            current_app.logger.info(f"[{play_id}] Serving playlist to { current_identity } for '{ token_data.token }' stream")
            return render_template('stream/stream.html', token=stream_token, stream_name=hls_key, pconfig=configuration.get_vars()['DEFAULT'])
    else:
        current_app.logger.info(f"[{play_id}] [{ remote_ip_address }]  with '{ current_identity }' footprint, tried to use the token '{ stream_token }' but isn't the owner.")
        return render_template('generic_advertence.html', 
                                title="¡Oops!",
                                message="Parece ser que este link ya está siendo usado por otra persona. Si crees que se trata de un error, por favor contactá al administrador"), 401