from flask import Blueprint, request, jsonify, g
from ..extensions import get_db
from ..services.auth_service import require_auth
from ..middleware.rate_limit import limiter
from datetime import datetime, timezone

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/profile", methods=["GET"])
@require_auth
def profile():
    user_id = g.user_id
    db = get_db()
    user_ref = db.collection("users").document(user_id)
    doc = user_ref.get()
    
    if not doc.exists:
        # Create a basic profile if they just signed up via Firebase
        user_data = {
            "email": g.user_email,
            "username": g.user_email.split('@')[0] if g.user_email else user_id,
            "preferences": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        user_ref.set(user_data)
        user_data["id"] = user_id
        return jsonify({"data": user_data, "meta": {}})
        
    user_data = doc.to_dict()
    user_data["id"] = doc.id
    return jsonify({"data": user_data, "meta": {}})

@auth_bp.route("/profile", methods=["PATCH"])
@require_auth
def update_profile():
    user_id = g.user_id
    db = get_db()
    user_ref = db.collection("users").document(user_id)
    doc = user_ref.get()
    
    if not doc.exists:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "User not found", "status": 404}}), 404
        
    try:
        req = request.get_json() or {}
        # Simple schema load, skipping strict validation for now since we removed SQLAlchemy models
        data = req 
    except Exception as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": str(err), "status": 400}}), 400
        
    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    user_data = doc.to_dict()
    
    if "username" in data:
        updates["username"] = data["username"]
        user_data["username"] = data["username"]
        
    if "preferences" in data:
        updates["preferences"] = data["preferences"]
        user_data["preferences"] = data["preferences"]
        
    user_ref.update(updates)
    user_data["id"] = user_id
    
    return jsonify({"data": user_data, "meta": {}})

@auth_bp.route("/account", methods=["DELETE"])
@require_auth
def delete_account():
    user_id = g.user_id
    db = get_db()
    
    # Delete user profile from Firestore
    db.collection("users").document(user_id).delete()
    
    # Optionally delete from Firebase Auth (this should usually happen client side, 
    # but we can do it here if using firebase_admin.auth.delete_user)
    from firebase_admin import auth
    try:
        auth.delete_user(user_id)
    except Exception as e:
        pass # Handle if user is already deleted
    
    return jsonify({"data": {"message": "Account deleted successfully."}, "meta": {}})
