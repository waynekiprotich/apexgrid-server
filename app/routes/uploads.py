import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory, g
from werkzeug.utils import secure_filename
from ..extensions import get_db
from ..services.auth_service import require_auth
import uuid

uploads_bp = Blueprint("uploads", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@uploads_bp.route("/avatars", methods=["POST"])
@require_auth
def upload_avatar():
    user_id = g.user_id
    db = get_db()
    user_ref = db.collection("users").document(user_id)
    doc = user_ref.get()
    
    if not doc.exists:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "User not found", "status": 404}}), 404

    if 'file' not in request.files:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "No file part", "status": 400}}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "No selected file", "status": 400}}), 400
        
    if file and allowed_file(file.filename):
        # Prevent oversized files via Flask's MAX_CONTENT_LENGTH, but let's be explicit
        file.seek(0, os.SEEK_END)
        size = file.tell()
        if size > 5 * 1024 * 1024: # 5MB
            return jsonify({"error": {"code": "PAYLOAD_TOO_LARGE", "message": "File size exceeds 5MB", "status": 413}}), 413
        file.seek(0)
            
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}")
        
        upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Delete old avatar if it exists
        user_data = doc.to_dict()
        if user_data.get("avatar_url"):
            old_filename = user_data["avatar_url"].split('/')[-1]
            old_path = os.path.join(upload_folder, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        
        url = f"/api/v1/uploads/avatars/{filename}"
        user_ref.update({"avatar_url": url})
        
        return jsonify({"data": {"avatar_url": url}, "meta": {}})
        
    return jsonify({"error": {"code": "BAD_REQUEST", "message": "Invalid file type", "status": 400}}), 400

@uploads_bp.route("/avatars/<filename>", methods=["GET"])
def get_avatar(filename):
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'avatars')
    return send_from_directory(upload_folder, secure_filename(filename))
