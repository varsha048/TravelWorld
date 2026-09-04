import os
from flask import Blueprint, request, jsonify, url_for
from werkzeug.utils import secure_filename
from auth_utils import token_required, admin_required
import time

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("", methods=["POST"])
@upload_bp.route("/", methods=["POST"])
@token_required
@admin_required
def upload_file():
    if 'file' not in request.files:
        return jsonify(status="fail", message="No file part in request"), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify(status="fail", message="No selected file"), 400
        
    if file and allowed_file(file.filename):
        # Create a safe, unique filename
        original_filename = secure_filename(file.filename)
        filename = f"{int(time.time())}_{original_filename}"
        
        # Determine upload path
        # Since this runs in backend-python, static/uploads should be there
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Since BASE_URL in frontend is /api/v1 (which maps to http://localhost:5000), 
        # we can just return the absolute path starting with http://localhost:5000/static/uploads/...
        # Alternatively, returning /static/uploads/filename is safer for both dev and prod.
        public_url = f"http://localhost:5000/static/uploads/{filename}"
        
        return jsonify(status="success", url=public_url), 201
        
    return jsonify(status="fail", message="Invalid file type"), 400
