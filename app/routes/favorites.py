from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.favorites import FavoriteDriver, FavoriteTeam

favorites_bp = Blueprint("favorites", __name__)

@favorites_bp.route("/drivers", methods=["GET"])
@jwt_required()
def get_favorite_drivers():
    user_id = get_jwt_identity()
    drivers = FavoriteDriver.query.filter_by(user_id=user_id).all()
    data = [{"id": d.id, "driver_number": d.driver_number, "created_at": d.created_at.isoformat()} for d in drivers]
    return jsonify({"data": data, "meta": {}})

@favorites_bp.route("/drivers", methods=["POST"])
@jwt_required()
def add_favorite_driver():
    user_id = get_jwt_identity()
    req = request.get_json() or {}
    driver_number = req.get("driver_number")
    
    if not driver_number:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "driver_number is required", "status": 400}}), 400
        
    if FavoriteDriver.query.filter_by(user_id=user_id, driver_number=driver_number).first():
        return jsonify({"error": {"code": "CONFLICT", "message": "Driver already favorited", "status": 409}}), 409
        
    fav = FavoriteDriver(user_id=user_id, driver_number=driver_number)
    db.session.add(fav)
    db.session.commit()
    
    return jsonify({"data": {"id": fav.id, "driver_number": fav.driver_number}, "meta": {}}), 201

@favorites_bp.route("/drivers/<int:driver_number>", methods=["DELETE"])
@jwt_required()
def delete_favorite_driver(driver_number):
    user_id = get_jwt_identity()
    fav = FavoriteDriver.query.filter_by(user_id=user_id, driver_number=driver_number).first()
    if not fav:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Favorite not found", "status": 404}}), 404
        
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"data": {"message": "Deleted"}, "meta": {}})

@favorites_bp.route("/teams", methods=["GET"])
@jwt_required()
def get_favorite_teams():
    user_id = get_jwt_identity()
    teams = FavoriteTeam.query.filter_by(user_id=user_id).all()
    data = [{"id": t.id, "team_name": t.team_name, "created_at": t.created_at.isoformat()} for t in teams]
    return jsonify({"data": data, "meta": {}})

@favorites_bp.route("/teams", methods=["POST"])
@jwt_required()
def add_favorite_team():
    user_id = get_jwt_identity()
    req = request.get_json() or {}
    team_name = req.get("team_name")
    
    if not team_name:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "team_name is required", "status": 400}}), 400
        
    if FavoriteTeam.query.filter_by(user_id=user_id, team_name=team_name).first():
        return jsonify({"error": {"code": "CONFLICT", "message": "Team already favorited", "status": 409}}), 409
        
    fav = FavoriteTeam(user_id=user_id, team_name=team_name)
    db.session.add(fav)
    db.session.commit()
    
    return jsonify({"data": {"id": fav.id, "team_name": fav.team_name}, "meta": {}}), 201

@favorites_bp.route("/teams/<team_name>", methods=["DELETE"])
@jwt_required()
def delete_favorite_team(team_name):
    user_id = get_jwt_identity()
    fav = FavoriteTeam.query.filter_by(user_id=user_id, team_name=team_name).first()
    if not fav:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Favorite not found", "status": 404}}), 404
        
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"data": {"message": "Deleted"}, "meta": {}})
