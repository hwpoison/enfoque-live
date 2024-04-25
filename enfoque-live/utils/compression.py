import gzip
from io import BytesIO 
from flask import request


exclude_files = (".ts")
def compress_response(response):
    if 'gzip' not in request.headers.get('Accept-Encoding', '') \
        or request.url.endswith(exclude_files):
            response.headers['Content-Length'] = len(response.get_data())
            return response

    response.direct_passthrough = False

    if (response.status_code < 200 or
        response.status_code >= 300 or
        'Content-Encoding' in response.headers):
        return response

    gzip_buffer = BytesIO()
    with gzip.GzipFile(mode='wb', compresslevel=9, fileobj=gzip_buffer) as gzip_file:
        gzip_file.write(response.get_data())

    # send
    response.set_data(gzip_buffer.getvalue())
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = len(response.get_data())

    return response
