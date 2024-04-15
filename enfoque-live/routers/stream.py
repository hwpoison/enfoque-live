from flask import Blueprint, jsonify, Response, render_template, request, current_app, redirect, url_for, current_app, make_response, send_from_directory
from utils import configuration
import database
import hashlib
from utils import auth
import os
import time

stream = Blueprint('stream', __name__)

def send_chunck(chunck_name=None):
    hls_path = configuration.get("HLS_DIR")
    if chunck_name is None:
        chunck_name = configuration.get("HLS_KEY")
    hls_fragment_full_path = hls_path + chunck_name
    if os.path.exists(hls_fragment_full_path):
        with open(hls_fragment_full_path, 'rb') as f:
            m3u8_content = f.read()
        return Response(m3u8_content, mimetype='application/vnd.apple.mpegurl')
    else:
        return "Stream content not found", 404

@stream.route('/monitoring')
@stream.route('/monitoring/<chunck_name>')
@auth.is_admin()
def monitorig(chunck_name=None):
    return send_chunck(chunck_name)


@stream.route('/status')
@auth.is_auth()
def isalive():
    playlist_location = f"{configuration.get('HLS_DIR')}{configuration.get('HLS_KEY')}"
    status_info = {
                "event_info":{'stream_title':configuration.get('STREAM_TITLE'), 
                "stream_date_info":configuration.get('STREAM_DATE_INFO'),
                "stream_subtitle":configuration.get('STREAM_SUBTITLE')}
    }

    if os.path.exists(playlist_location):
        status_info['status'] = "online"
        return jsonify(status_info), 200

    status_info['status'] = "offline"
    return jsonify(status_info), 503

@stream.route('/play/<stream_token>')
@stream.route('/play/<stream_token>/<chunck_name>')
def play(stream_token, chunck_name=None):
    hls_key = configuration.get("HLS_KEY")

    # Generate the request footprint that will be setted as identify
    remote_ip_address = request.remote_addr
    hash_string = f"{remote_ip_address}{stream_token}"
    
    # md5(IP + Requested Token)
    footprint = hashlib.md5(hash_string.encode()).hexdigest()

    # Check if request has a token
    auth.verify_jwt_in_request(optional=True)
    current_identity = auth.get_identity()
    current_app.logger.info(
        f"Incoming connection from '{ remote_ip_address }' with '{ current_identity }' identity")

    # if not assign the current footprint as identity and redirect to itself
    if current_identity == None:
        print(f"Doens't have identity, assigning one: {footprint}")
        identity = {'role':'client', 'footprint':footprint}
        access_token = auth.create_access_token(identity=identity)
        send_jwt = make_response(redirect(url_for("stream.play", token=stream_token)))
        auth.set_access_cookies(send_jwt, access_token)
        return send_jwt

    # current request identity
    identity_role = current_identity.get('role')
    identity_footprint = current_identity.get('footprint')

    # get requested token info
    token_data = database.dump_token(stream_token)
    if token_data is None:
        return render_template('generic_advertence.html', 
                                title="Error", 
                                message="Este link no es valido o ha sido eliminado. ⛓️‍💥")
    else:
        if token_data['banned']:
            return render_template('generic_advertence.html', 
                                    title="Error", 
                                    message="Este link ya no está disponible. ⛓️‍💥")

        # if the token is not claimed, claim it
        if token_data['footprint'] == None \
                                    and identity_role != "admin" \
                                    and current_identity != None:
            database.set_footprint(token_data['token'], identity_footprint)
            current_app.logger.info(f" [{ remote_ip_address }]  { current_identity } claimed '{ stream_token }' stream.")

    # starts the verification
    token_data = database.dump_token(stream_token)  # reload
    if token_data['footprint'] == identity_footprint \
        or token_data['footprint'] == footprint \
            or identity_role == "admin" \
                or configuration.get('FREE_MODE') == 'enabled':
        print(f"sending chunck to '{ current_identity }'")
        if chunck_name:
            return send_chunck(chunck_name)
        else:  # Serve the playlist
            print(f"Serving playlist to { current_identity } for '{ token_data['token'] }' stream")
            return render_template('stream.html', token=stream_token, stream_name=hls_key, pconfig=configuration.get_vars(), )
    else:
        current_app.logger.info(
            f"[{ remote_ip_address }]  with '{ current_identity }' footprint, tried to use the token '{ stream_token }' but isn't the owner.")
        return render_template('generic_advertence.html', 
                                title="¡Oops!",
                                message="Parece ser que este link ya está siendo usado por otra persona. Si crees que se trata de un error, por favor contactá al administrador"), 401
    return "Bad request", 403
