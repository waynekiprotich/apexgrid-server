from functools import wraps
from flask import request, jsonify, g
from firebase_admin import auth

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Missing or invalid token"}}), 401
        
        token = auth_header.split(" ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            g.user_id = decoded_token['uid']
            g.user_email = decoded_token.get('email')
        except Exception as e:
            return jsonify({"error": {"code": "UNAUTHORIZED", "message": f"Invalid token: {str(e)}"}}), 401
            
        return f(*args, **kwargs)
    return decorated_function
