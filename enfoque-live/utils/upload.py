from flask import current_app
from werkzeug.utils import secure_filename
import werkzeug
import os


ALLOWED_EXTENSIONS = {'jpg','png','jpeg','webp','bmp','gif'}

def allowed_file(filename : str) -> None:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file : werkzeug.datastructures.file_storage.FileStorage, target_name : str =None):
    if not file:
        return False

    if file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        if target_name:
            filename = f"{target_name}{extension}"
        full_save_path = f"{ current_app.config['UPLOAD_FOLDER'] }/images/{filename}"
        file.save(full_save_path)

    return full_save_path
