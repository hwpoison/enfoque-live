from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, current_app, make_response

import hashlib, os
from utils import auth, tokens
from utils import configuration
from utils import stream_dispatcher 
from models import tokens as tokens_db
from models import viewers

from utils.limiter import limiter
stream = Blueprint('stream', __name__)

@stream.route('/monitoring')
@stream.route('/monitoring/<chunk_name>')
@auth.is_auth("admin")
def monitorig(chunk_name=None):
    return stream_dispatcher.send_chunk(chunk_name)


@stream.route(f'/get/{configuration.get("cdn_origin_secret_token", "cdn")}/<chunk_name>')
def stream_playlist(chunk_name=None):
    response = stream_dispatcher.send_chunk(chunk_name)
    if chunk_name.endswith('.m3u8'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


@stream.route('/status/<stream_token>')
@limiter.limit("4 per 10 seconds")
@auth.is_auth('admin', 'client')
def stream_status(stream_token: str):
    """
    Handles stream status info
    :param stream_token: The stream token

    """
    playlist_location = f"{configuration.get('default_dir', 'hls')}{configuration.get('playlist_name', 'hls')}"
    try:
        viewers.i_am_watching(stream_token)
        total_current_viewers = viewers.get_current_viewers()
        status_info = {
            "event_info":{
                'stream_title': configuration.get('title', 'stream'), 
                "stream_date_info": configuration.get('date_info', 'stream'),
                "stream_subtitle": configuration.get('subtitule', 'stream'),
                "player_poster_image": configuration.get('player_poster_image', 'stream'),
            },
            "stream":{
                'current_viewers': total_current_viewers,
            }
        }

        # If the playlist exists, means that currently there is a streaming in progress
        if os.path.exists(playlist_location):
            status_info['stream']['status'] = "online"
        else:
            status_info['stream']['status'] = "offline"

        # runtime cdn change
        stream_mode = configuration.get('mode', 'stream')
        if stream_mode == 'rtmp_cdn':
             status_info['stream']['cdnURL'] = f"{configuration.get('rtmp_cdn_url', 'cdn')}/get/{configuration.get('playlist_name', 'hls')}"
        
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
    hls_key = configuration.get("playlist_name", 'hls')

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
                or configuration.get('free_mode', 'purchase') == 'enabled':
        if chunk_name:
            return stream_dispatcher.send_chunk(chunk_name)
        else:  # Serve the main view / playlist
            current_app.logger.info(f"[{play_id}] Serving playlist to { current_identity } for '{ token_data.token }' stream")
            return render_template('stream/stream.html', token=stream_token, stream_name=hls_key, pconfig=configuration.get_vars())
    else:
        current_app.logger.info(f"[{play_id}] [{ remote_ip_address }]  with '{ current_identity }' footprint, tried to use the token '{ stream_token }' but isn't the owner.")
        return render_template('generic_advertence.html', 
                                title="¡Oops!",
                                message="Parece ser que este link ya está siendo usado por otra persona. Si crees que se trata de un error, por favor contactá al administrador"), 401