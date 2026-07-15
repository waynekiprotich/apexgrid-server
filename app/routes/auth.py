from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from ..extensions import db
from ..models.user import User
from ..schemas.user_schema import user_schema, register_schema, login_schema, password_reset_request_schema, password_reset_schema, update_profile_schema
from ..services.auth_service import hash_password, check_password, generate_tokens, revoke_refresh_token, verify_refresh_token, generate_password_reset_token, verify_and_use_password_reset_token, update_password
from ..middleware.rate_limit import limiter
from ..middleware.auth import admin_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": err.messages, "status": 400}}), 400
        
    if User.query.filter_by(email=data["email"]).first() or User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": {"code": "CONFLICT", "message": "User already exists", "status": 409}}), 409
        
    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hash_password(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"data": user_schema.dump(user), "meta": {}}), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": err.messages, "status": 400}}), 400
        
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password(data["password"], user.password_hash):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Invalid credentials", "status": 401}}), 401
        
    access_token, raw_token, token_id = generate_tokens(user.id)
    
    resp = make_response(jsonify({"data": {"access_token": access_token}, "meta": {}}))
    resp.set_cookie(
        "refresh_token", 
        f"{token_id}:{raw_token}",
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=7*24*60*60
    )
    return resp

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    cookie_token = request.cookies.get("refresh_token")
    if not cookie_token or ":" not in cookie_token:
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Invalid refresh token", "status": 401}}), 401
        
    token_id, raw_token = cookie_token.split(":", 1)
    rt = verify_refresh_token(token_id, raw_token)
    
    if not rt:
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired refresh token", "status": 401}}), 401
        
    access_token, new_raw_token, new_token_id = generate_tokens(rt.user_id)
    revoke_refresh_token(token_id, rt.user_id) 
    
    resp = make_response(jsonify({"data": {"access_token": access_token}, "meta": {}}))
    resp.set_cookie(
        "refresh_token", 
        f"{new_token_id}:{new_raw_token}",
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=7*24*60*60
    )
    return resp

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    cookie_token = request.cookies.get("refresh_token")
    if cookie_token and ":" in cookie_token:
        token_id, _ = cookie_token.split(":", 1)
        revoke_refresh_token(token_id, user_id)
        
    resp = make_response(jsonify({"data": {"message": "Logged out"}, "meta": {}}))
    resp.delete_cookie("refresh_token")
    return resp

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "User not found", "status": 404}}), 404
    return jsonify({"data": user_schema.dump(user), "meta": {}})

@auth_bp.route("/profile", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "User not found", "status": 404}}), 404
        
    try:
        data = update_profile_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": err.messages, "status": 400}}), 400
        
    if "username" in data:
        if User.query.filter(User.username == data["username"], User.id != user_id).first():
            return jsonify({"error": {"code": "CONFLICT", "message": "Username already taken", "status": 409}}), 409
        user.username = data["username"]
        
    if "preferences" in data:
        user.preferences = data["preferences"]
        
    db.session.commit()
    return jsonify({"data": user_schema.dump(user), "meta": {}})

@auth_bp.route("/request-password-reset", methods=["POST"])
@limiter.limit("3 per hour")
def request_password_reset():
    try:
        data = password_reset_request_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": err.messages, "status": 400}}), 400
        
    user = User.query.filter_by(email=data["email"]).first()
    if user:
        raw_token, token_id = generate_password_reset_token(user.id)
        # Mocking email send
        from flask import current_app
        current_app.logger.info(f"Password reset token for {user.email}: {token_id}:{raw_token}")
        
    # Always return 200 to prevent email enumeration
    return jsonify({"data": {"message": "If an account exists, a reset link has been sent."}, "meta": {}})

@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per hour")
def reset_password():
    try:
        data = password_reset_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": err.messages, "status": 400}}), 400
        
    token_str = data["token"]
    if ":" not in token_str:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Invalid token format", "status": 400}}), 400
        
    token_id, raw_token = token_str.split(":", 1)
    prt = verify_and_use_password_reset_token(token_id, raw_token)
    
    if not prt:
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired token", "status": 401}}), 401
        
    update_password(prt.user_id, data["new_password"])
    
    return jsonify({"data": {"message": "Password successfully updated."}, "meta": {}})

@auth_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "User not found", "status": 404}}), 404
        
    db.session.delete(user)
    db.session.commit()
    
    resp = make_response(jsonify({"data": {"message": "Account deleted successfully."}, "meta": {}}))
    resp.delete_cookie("refresh_token")
    return resp
