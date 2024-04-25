from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for, current_app, make_response, send_file

import hashlib
import time, datetime
import os

from utils import auth, tokens
from utils import configuration
from models import tokens as tokens_db
from models import viewers as visit_counter_db

stream = Blueprint('stream', __name__)

def send_chunck(chunk_name=None):
    hls_path = configuration.get("hls_dir")
    if chunk_name is None:
        chunk_name = configuration.get("hls_key")

    response = make_response()
    hls_fragment_full_path = os.path.join(hls_path, chunk_name)

    if os.path.isfile(hls_fragment_full_path):
        return make_response(send_file(hls_fragment_full_path, mimetype='application/vnd.apple.mpegurl'))
    elif os.path.isfile(hls_fragment_full_path + '.gz'):
        with open(hls_fragment_full_path + '.gz', 'rb') as f:
            m3u8_content = f.read()
            response = make_response(m3u8_content)
            response.mimetype = 'application/vnd.apple.mpegurl'
            response.headers['Content-Encoding'] = 'gzip'
            return response
    else:
        return "Stream fragment not found", 404

@stream.route('/monitoring')
@stream.route('/monitoring/<chunck_name>')
@auth.is_admin()
def monitorig(chunck_name=None):
    return send_chunck(chunck_name)


@stream.route('/status/<stream_token>')
@auth.is_auth()
def isalive(stream_token : str):
    visit_counter_db.get_or_create_session(stream_token,'enfoque_live')
    current_viewers = visit_counter_db.count_recent_visits('enfoque_live')
    playlist_location = f"{configuration.get('hls_dir')}{configuration.get('hls_key')}"
    status_info = {
       
        "event_info":{
            'current_viewers':current_viewers,
            'stream_title':configuration.get('stream_title'), 
            "stream_date_info":configuration.get('stream_date_info'),
            "stream_subtitle":configuration.get('stream_subtitule'),
            "player_poster_image":configuration.get('player_poster_image')
        }
    }

    if os.path.exists(playlist_location):
        status_info['status'] = "online"
        return jsonify(status_info), 200

    status_info['status'] = "offline"
    return jsonify(status_info), 503

@stream.route('/play/<stream_token>')
@stream.route('/play/<stream_token>/<chunck_name>')
async def play(stream_token, chunck_name=None):
    play_id = tokens.generate_error_id()

    hls_key = configuration.get("hls_key")

    # Generate the request footprint that will be setted as identify
    remote_ip_address = request.remote_addr
    hash_string = f"{remote_ip_address}{stream_token}"
    
    # md5(IP + Requested Token)
    footprint = hashlib.md5(hash_string.encode()).hexdigest()

    # Check if request has a token
    auth.verify_jwt_in_request(optional=True)
    current_identity = auth.get_identity()
    current_app.logger.info(
        f"[{play_id}] Incoming connection from '{ remote_ip_address }' with '{ current_identity }' identity")

    # if not assign the current footprint as identity and redirect to itself
    if current_identity == None:
        current_app.logger.info(f"[{play_id}] Doens't have identity, assigning one: {footprint}")
        identity = {'role':'client', 'footprint':footprint}
        expires = datetime.timedelta(days=7)
        access_token = auth.create_access_token(identity=identity, expires_delta=expires)
        send_jwt = make_response(redirect(url_for("stream.play", stream_token=stream_token)))
        auth.set_access_cookies(send_jwt, access_token)
        return send_jwt

    # current request identity
    identity_role = current_identity.get('role')
    identity_footprint = current_identity.get('footprint')

    # get requested token info
    token_data = tokens_db.get(stream_token)

    if token_data is None:
        current_app.logger.error(f"[{play_id}] The token '{stream_token}' doens't exists")
        return render_template('generic_advertence.html', 
                                error_id=play_id,
                                title="Error", 
                                message="Este enlace no es valido o ha sido eliminado. ⛓️‍💥"), 404
    else:
        if token_data.banned:
            return render_template('generic_advertence.html', 
                                    title="Error", 
                                    message="Este enlace ha sido deshabilitado. ⛓️‍💥"), 404

        # if the token is not claimed, claim it
        if token_data.footprint == None \
                                    and identity_role != "admin" \
                                    and current_identity != None:
            token_data.footprint = identity_footprint
            tokens_db.save()
            current_app.logger.info(f"[{play_id}] [{ remote_ip_address }]  { current_identity } claimed '{ stream_token }' stream.")

    # starts the verification
    if token_data.footprint == identity_footprint \
        or token_data.footprint == footprint \
            or identity_role == "admin" \
                or configuration.get('free_mode') == 'enabled':
        if chunck_name:
            return send_chunck(chunck_name)
        else:  # Serve the playlist
            current_app.logger.info(f"[{play_id}] Serving playlist to { current_identity } for '{ token_data.token }' stream")
            return render_template('stream.html', token=stream_token, stream_name=hls_key, pconfig=configuration.get_vars()['DEFAULT'])
    else:
        current_app.logger.info(
            f"[{play_id}] [{ remote_ip_address }]  with '{ current_identity }' footprint, tried to use the token '{ stream_token }' but isn't the owner.")
        return render_template('generic_advertence.html', 
                                title="¡Oops!",
                                message="Parece ser que este link ya está siendo usado por otra persona. Si crees que se trata de un error, por favor contactá al administrador"), 401