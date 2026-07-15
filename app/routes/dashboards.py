from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.dashboard import SavedDashboard

dashboards_bp = Blueprint("dashboards", __name__)

@dashboards_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboards():
    user_id = get_jwt_identity()
    dashboards = SavedDashboard.query.filter_by(user_id=user_id).all()
    data = [{"id": d.id, "name": d.dashboard_name, "filters": d.filters} for d in dashboards]
    return jsonify({"data": data, "meta": {}})

@dashboards_bp.route("/", methods=["POST"])
@jwt_required()
def create_dashboard():
    user_id = get_jwt_identity()
    req = request.get_json() or {}
    name = req.get("name")
    
    if not name:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Dashboard name is required", "status": 400}}), 400
        
    dashboard = SavedDashboard(user_id=user_id, dashboard_name=name, filters=req.get("filters", {}))
    db.session.add(dashboard)
    db.session.commit()
    
    return jsonify({"data": {"id": dashboard.id, "name": dashboard.dashboard_name, "filters": dashboard.filters}, "meta": {}}), 201

@dashboards_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_dashboard(id):
    user_id = get_jwt_identity()
    d = SavedDashboard.query.filter_by(id=id, user_id=user_id).first()
    if not d:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Dashboard not found", "status": 404}}), 404
    return jsonify({"data": {"id": d.id, "name": d.dashboard_name, "filters": d.filters}, "meta": {}})

@dashboards_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_dashboard(id):
    user_id = get_jwt_identity()
    d = SavedDashboard.query.filter_by(id=id, user_id=user_id).first()
    if not d:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Dashboard not found", "status": 404}}), 404
        
    req = request.get_json() or {}
    if "name" in req:
        d.dashboard_name = req["name"]
    if "filters" in req:
        d.filters = req["filters"]
        
    db.session.commit()
    return jsonify({"data": {"id": d.id, "name": d.dashboard_name, "filters": d.filters}, "meta": {}})

@dashboards_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_dashboard(id):
    user_id = get_jwt_identity()
    d = SavedDashboard.query.filter_by(id=id, user_id=user_id).first()
    if not d:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Dashboard not found", "status": 404}}), 404
        
    db.session.delete(d)
    db.session.commit()
    return jsonify({"data": {"message": "Deleted"}, "meta": {}})
