from flask import send_file, make_response
import os
import utils.configuration as configuration


def get_mimetype(file_path: str) -> str:
    """
        Returns the mimetype based on file name
    """
    if file_path.endswith('.m3u8'):
        return 'application/x-mpegURL'
    elif file_path.endswith('.ts'):
        return 'application/x-mpegURL'
    else:
        return 'application/octet-stream'


def send_chunk(chunk_name: str = None) -> tuple:
    """
    Sends a chunk of the HLS stream.
    """
    hls_path = configuration.get("hls_dir")
    if chunk_name is None:
        chunk_name = configuration.get("hls_key")

    hls_fragment_full_path = os.path.join(hls_path, chunk_name)
    mimetype = get_mimetype(hls_fragment_full_path)

    if os.path.isfile(hls_fragment_full_path):
        return send_file(hls_fragment_full_path, mimetype=mimetype)
    
    # for compressed chunks
    elif os.path.isfile(hls_fragment_full_path + '.gz'):
        with open(hls_fragment_full_path + '.gz', 'rb') as f:
            content = f.read()
            response = make_response(content)
            response.mimetype = mimetype
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.get_data())
            return response, 203
    else:
        return "Stream content not found", 404
