from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone
from ..extensions import get_db
from ..services.auth_service import require_auth
import uuid

dashboards_bp = Blueprint("dashboards", __name__)

@dashboards_bp.route("/", methods=["GET"])
@require_auth
def get_dashboards():
    user_id = g.user_id
    db = get_db()
    docs = db.collection("users").document(user_id).collection("saved_dashboards").stream()
    
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({"id": doc.id, "name": d.get("dashboard_name"), "filters": d.get("filters", {})})
    return jsonify({"data": data, "meta": {}})

@dashboards_bp.route("/", methods=["POST"])
@require_auth
def create_dashboard():
    user_id = g.user_id
    req = request.get_json() or {}
    name = req.get("name")
    
    if not name:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Dashboard name is required", "status": 400}}), 400
        
    db = get_db()
    doc_id = str(uuid.uuid4())
    dash_ref = db.collection("users").document(user_id).collection("saved_dashboards").document(doc_id)
    
    filters = req.get("filters", {})
    dash_data = {
        "dashboard_name": name,
        "filters": filters,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    dash_ref.set(dash_data)
    
    return jsonify({"data": {"id": doc_id, "name": name, "filters": filters}, "meta": {}}), 201

@dashboards_bp.route("/<id>", methods=["GET"])
@require_auth
def get_dashboard(id):
    user_id = g.user_id
    db = get_db()
    dash_ref = db.collection("users").document(user_id).collection("saved_dashboards").document(id)
    doc = dash_ref.get()
    
    if not doc.exists:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Dashboard not found", "status": 404}}), 404
        
    d = doc.to_dict()
    return jsonify({"data": {"id": doc.id, "name": d.get("dashboard_name"), "filters": d.get("filters", {})}, "meta": {}})

@dashboards_bp.route("/<id>", methods=["PATCH"])
@require_auth
def update_dashboard(id):
    user_id = g.user_id
    db = get_db()
    dash_ref = db.collection("users").document(user_id).collection("saved_dashboards").document(id)
    doc = dash_ref.get()
    
    if not doc.exists:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Dashboard not found", "status": 404}}), 404
        
    req = request.get_json() or {}
    d = doc.to_dict()
    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if "name" in req:
        updates["dashboard_name"] = req["name"]
        d["dashboard_name"] = req["name"]
    if "filters" in req:
        updates["filters"] = req["filters"]
        d["filters"] = req["filters"]
        
    dash_ref.update(updates)
    return jsonify({"data": {"id": doc.id, "name": d.get("dashboard_name"), "filters": d.get("filters", {})}, "meta": {}})

@dashboards_bp.route("/<id>", methods=["DELETE"])
@require_auth
def delete_dashboard(id):
    user_id = g.user_id
    db = get_db()
    dash_ref = db.collection("users").document(user_id).collection("saved_dashboards").document(id)
    
    if not dash_ref.get().exists:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Dashboard not found", "status": 404}}), 404
        
    dash_ref.delete()
    return jsonify({"data": {"message": "Deleted"}, "meta": {}})
