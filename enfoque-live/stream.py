from flask import Blueprint, Response, render_template, request, current_app, redirect, url_for, current_app, make_response, send_from_directory
import configuration
import database
import hashlib
import auth
import os

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


@stream.route('/play/<token>')
@stream.route('/play/<token>/<chunck_name>')
def play(token, chunck_name=None):
    hls_key = configuration.get("HLS_KEY")
    auth.verify_jwt_in_request(optional=True)

    # Generate the request footprint that will be setted as identify
    remote_ip_address = request.remote_addr
    hash_string = f"{remote_ip_address}{token}"
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
        access_token = auth.create_access_token(identity=footprint)
        send_jwt = make_response(redirect(url_for("stream.play", token=token)))
        auth.set_access_cookies(send_jwt, access_token)
        return send_jwt

    # get requested token info
    token_data = database.dump_token(token)
    if token_data is None:
        return render_template('invalid_token.html')
    else:
        if token_data['banned']:
            return render_template('banned_token.html')
        # if the token is not claimed, claim it
        if token_data['footprint'] == None and current_identity != "admin" and current_identity != None:  # claim the token
            current_app.logger.info(
                f" [{ remote_ip_address }] token '{ token }' claimed by { current_identity }")
            database.set_footprint(token_data['token'], current_identity)

    # starts the verification
    token_data = database.dump_token(token)  # reload
    if token_data['footprint'] == current_identity \
        or token_data['footprint'] == footprint \
            or current_identity == "admin" \
                or configuration.get('FREE_MODE') == 'enabled':
        print(
            f"Request '{current_identity}' match with footprint from token that is '{token_data['footprint']}'")
        if chunck_name:
            return send_chunck(chunck_name)
        else:  # Serve the playlist
            print(
                f"Serving playlist to {current_identity} for { token_data['token'] }")
            return render_template('stream.html', token=token, stream_name=hls_key, pconfig=configuration.get_vars(), )
    else:
        current_app.logger.info(
            f"[{ remote_ip_address }]  with '{ current_identity }' footprint, tried to use the token '{ token }' but isn't the owner.")
        return render_template('holded_error.html'), 401

    return "Bad request", 403
