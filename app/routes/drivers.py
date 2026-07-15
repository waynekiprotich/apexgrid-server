from flask import Blueprint, request, jsonify
from ..services import cache_service, openf1_client

drivers_bp = Blueprint("drivers", __name__)

@drivers_bp.route("/drivers", methods=["GET"])
def list_drivers():
    season = request.args.get("season")
    cached = cache_service.get("drivers", season=season)
    if cached:
        return jsonify({"data": cached, "meta": {"cached": True}})
    
    data = []
    if season:
        # OpenF1 drivers endpoint doesn't support season directly.
        # We find a session for that year, and fetch its drivers.
        sessions = openf1_client.get("/v1/sessions", params={"year": season})
        if sessions:
            # use the last session's key
            session_key = sessions[-1].get("session_key")
            data = openf1_client.get("/v1/drivers", params={"session_key": session_key})
    else:
        # Just get some recent drivers if no season
        data = openf1_client.get("/v1/drivers", params={"session_key": "latest"})

    cache_service.set("drivers", data, ttl_seconds=86400, season=season)
    
    return jsonify({"data": data, "meta": {"cached": False}})

@drivers_bp.route("/drivers/<int:driver_number>", methods=["GET"])
def get_driver(driver_number):
    season = request.args.get("season")
    cached = cache_service.get("driver", driver_number=driver_number, season=season)
    if cached:
        return jsonify({"data": cached, "meta": {"cached": True}})
        
    if season:
        sessions = openf1_client.get("/v1/sessions", params={"year": season})
        if sessions:
            session_key = sessions[-1].get("session_key")
            data = openf1_client.get("/v1/drivers", params={"driver_number": driver_number, "session_key": session_key})
        else:
            data = []
    else:
        data = openf1_client.get("/v1/drivers", params={"driver_number": driver_number, "session_key": "latest"})
        
    driver = data[-1] if data else None
    if not driver:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Driver not found", "status": 404}}), 404
        
    cache_service.set("driver", driver, ttl_seconds=86400, driver_number=driver_number, season=season)
    
    return jsonify({"data": driver, "meta": {"cached": False}})
