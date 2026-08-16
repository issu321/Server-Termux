from flask import Blueprint, send_from_directory, abort
import os

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/<path:filename>')
def uploaded_file(filename):
    if not os.path.exists(filename):
        abort(404)
    return send_from_directory('.', filename)