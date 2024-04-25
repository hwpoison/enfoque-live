import os, time, gzip
from utils import configuration

"""
This script will compress in loop every hls chunk except the *.m3u8 
and the last one that is in process of generation.

This is optional to the app but will help to compress video chunks with a low entropy.

"""

default_extensions = ('.ts')
hls_dir = configuration.get("hls_dir")

def gzip_file(file_path):
    new_name = f"{file_path}.gz"
    with open(file_path, 'rb') as f_in:
        with gzip.open(new_name, 'wb') as f_out:
            f_out.writelines(f_in)
    os.remove(file_path)

print(f"HLS Compressor started. All files under '{ hls_dir }' are being compressed")

while True:
    try:
        all_ts_files = [os.path.join(hls_dir, file) for file in os.listdir(hls_dir) if file.endswith(default_extensions) and os.path.isfile(os.path.join(hls_dir, file))]
        sorted_by_date = sorted(all_ts_files, key=os.path.getmtime, reverse=False)
        for m in sorted_by_date[:-1]:
            gzip_file(m)
        time.sleep(3)
    except Exception as e:
        print("Error to compress", e)
