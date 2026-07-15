from functools import wraps
from flask import jsonify, g
from ..extensions import get_db

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not hasattr(g, 'user_id'):
                return jsonify({"error": {"code": "FORBIDDEN", "message": "Admin access required", "status": 403}}), 403
                
            db = get_db()
            user_ref = db.collection("users").document(g.user_id)
            doc = user_ref.get()
            
            if not doc.exists or not doc.to_dict().get("is_admin", False):
                return jsonify({"error": {"code": "FORBIDDEN", "message": "Admin access required", "status": 403}}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
