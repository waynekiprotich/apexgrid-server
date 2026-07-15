from flask import Blueprint, request, jsonify
from ..services.openf1_client import fetch_with_cache

sessions_bp = Blueprint("sessions", __name__)

@sessions_bp.route("/sessions", methods=["GET"])
def get_sessions():
    year = request.args.get("year")
    country = request.args.get("country")
    session_type = request.args.get("session_type")
    
    data, cached = fetch_with_cache("sessions", "/v1/sessions", 86400, year=year, country_name=country, session_name=session_type)
    return jsonify({"data": data, "meta": {"cached": cached}})

@sessions_bp.route("/sessions/<session_key>", methods=["GET"])
def get_session(session_key):
    data, cached = fetch_with_cache("session_detail", "/v1/sessions", 86400, session_key=session_key)
    if not data:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Session not found", "status": 404}}), 404
    return jsonify({"data": data[0], "meta": {"cached": cached}})

@sessions_bp.route("/sessions/<session_key>/weather", methods=["GET"])
def get_weather(session_key):
    data, cached = fetch_with_cache("weather", "/v1/weather", 60, session_key=session_key)
    return jsonify({"data": data, "meta": {"cached": cached}})

@sessions_bp.route("/sessions/<session_key>/pitstops", methods=["GET"])
def get_pitstops(session_key):
    data, cached = fetch_with_cache("pitstops", "/v1/pit", 60, session_key=session_key)
    return jsonify({"data": data, "meta": {"cached": cached}})

@sessions_bp.route("/sessions/<session_key>/intervals", methods=["GET"])
def get_intervals(session_key):
    data, cached = fetch_with_cache("intervals", "/v1/intervals", 60, session_key=session_key)
    return jsonify({"data": data, "meta": {"cached": cached}})
@sessions_bp.route("/sessions/<session_key>/laps", methods=["GET"])
def get_laps(session_key):
    driver_number = request.args.get("driver_number")
    data, cached = fetch_with_cache("laps", "/v1/laps", 60, session_key=session_key, driver_number=driver_number)
    return jsonify({"data": data, "meta": {"cached": cached}})

@sessions_bp.route("/sessions/<session_key>/racecontrol", methods=["GET"])
def get_racecontrol(session_key):
    data, cached = fetch_with_cache("race_control", "/v1/race_control", 60, session_key=session_key)
    return jsonify({"data": data, "meta": {"cached": cached}})

@sessions_bp.route("/sessions/<session_key>/tyres", methods=["GET"])
def get_tyres(session_key):
    data, cached = fetch_with_cache("stints", "/v1/stints", 60, session_key=session_key)
    return jsonify({"data": data, "meta": {"cached": cached}})
