from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone
from ..extensions import get_db
from ..services.auth_service import require_auth

favorites_bp = Blueprint("favorites", __name__)

@favorites_bp.route("/drivers", methods=["GET"])
@require_auth
def get_favorite_drivers():
    user_id = g.user_id
    db = get_db()
    docs = db.collection("users").document(user_id).collection("favorite_drivers").stream()
    
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({
            "id": doc.id,
            "driver_number": d.get("driver_number"),
            "created_at": d.get("created_at")
        })
    return jsonify({"data": data, "meta": {}})

@favorites_bp.route("/drivers", methods=["POST"])
@require_auth
def add_favorite_driver():
    user_id = g.user_id
    req = request.get_json() or {}
    driver_number = req.get("driver_number")
    
    if not driver_number:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "driver_number is required", "status": 400}}), 400
        
    db = get_db()
    fav_ref = db.collection("users").document(user_id).collection("favorite_drivers").document(str(driver_number))
    
    if fav_ref.get().exists:
        return jsonify({"error": {"code": "CONFLICT", "message": "Driver already favorited", "status": 409}}), 409
        
    fav_data = {
        "driver_number": driver_number,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    fav_ref.set(fav_data)
    
    return jsonify({"data": {"id": str(driver_number), "driver_number": driver_number}, "meta": {}}), 201

@favorites_bp.route("/drivers/<int:driver_number>", methods=["DELETE"])
@require_auth
def delete_favorite_driver(driver_number):
    user_id = g.user_id
    db = get_db()
    fav_ref = db.collection("users").document(user_id).collection("favorite_drivers").document(str(driver_number))
    
    if not fav_ref.get().exists:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Favorite not found", "status": 404}}), 404
        
    fav_ref.delete()
    return jsonify({"data": {"message": "Deleted"}, "meta": {}})

@favorites_bp.route("/teams", methods=["GET"])
@require_auth
def get_favorite_teams():
    user_id = g.user_id
    db = get_db()
    docs = db.collection("users").document(user_id).collection("favorite_teams").stream()
    
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({
            "id": doc.id,
            "team_name": d.get("team_name"),
            "created_at": d.get("created_at")
        })
    return jsonify({"data": data, "meta": {}})

@favorites_bp.route("/teams", methods=["POST"])
@require_auth
def add_favorite_team():
    user_id = g.user_id
    req = request.get_json() or {}
    team_name = req.get("team_name")
    
    if not team_name:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "team_name is required", "status": 400}}), 400
        
    db = get_db()
    # Use team name as document ID, safely replacing spaces
    doc_id = str(team_name).replace(" ", "_")
    fav_ref = db.collection("users").document(user_id).collection("favorite_teams").document(doc_id)
    
    if fav_ref.get().exists:
        return jsonify({"error": {"code": "CONFLICT", "message": "Team already favorited", "status": 409}}), 409
        
    fav_data = {
        "team_name": team_name,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    fav_ref.set(fav_data)
    
    return jsonify({"data": {"id": doc_id, "team_name": team_name}, "meta": {}}), 201

@favorites_bp.route("/teams/<team_name>", methods=["DELETE"])
@require_auth
def delete_favorite_team(team_name):
    user_id = g.user_id
    db = get_db()
    doc_id = str(team_name).replace(" ", "_")
    fav_ref = db.collection("users").document(user_id).collection("favorite_teams").document(doc_id)
    
    if not fav_ref.get().exists:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Favorite not found", "status": 404}}), 404
        
    fav_ref.delete()
    return jsonify({"data": {"message": "Deleted"}, "meta": {}})

