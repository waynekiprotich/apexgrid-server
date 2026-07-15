from flask import Blueprint, jsonify, request
from ..services.openf1_client import fetch_with_cache

telemetry_bp = Blueprint("telemetry", __name__)

@telemetry_bp.route("/sessions/<session_key>/telemetry", methods=["GET"])
def get_telemetry(session_key):
    driver_number = request.args.get("driver_number")
    # telemetry can be huge, lower cache TTL
    data, cached = fetch_with_cache("car_data", "/v1/car_data", 60, session_key=session_key, driver_number=driver_number)
    return jsonify({"data": data, "meta": {"cached": cached}})
    
@telemetry_bp.route("/sessions/<session_key>/location", methods=["GET"])
def get_location(session_key):
    driver_number = request.args.get("driver_number")
    data, cached = fetch_with_cache("location", "/v1/location", 60, session_key=session_key, driver_number=driver_number)
    return jsonify({"data": data, "meta": {"cached": cached}})
