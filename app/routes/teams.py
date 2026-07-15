from flask import Blueprint, jsonify, request
from ..services import openf1_client
from ..services.openf1_client import fetch_with_cache

teams_bp = Blueprint("teams", __name__)

@teams_bp.route("/teams", methods=["GET"])
def get_teams():
    # OpenF1 drivers require session_key, not year.
    year = request.args.get("year", "2024")
    sessions = openf1_client.get("/v1/sessions", params={"year": year})
    if not sessions:
        return jsonify({"data": [], "meta": {"cached": False}})
        
    session_key = sessions[-1].get("session_key")
    data, cached = fetch_with_cache("drivers_for_teams", "/v1/drivers", 86400, session_key=session_key)
    
    if data:
        # Extract unique teams
        teams_map = {}
        for driver in data:
            team_name = driver.get("team_name")
            if team_name and team_name not in teams_map:
                teams_map[team_name] = {
                    "team_name": team_name,
                    "team_colour": driver.get("team_colour"),
                    "drivers": []
                }
            if team_name:
                teams_map[team_name]["drivers"].append(driver.get("driver_number"))
        return jsonify({"data": list(teams_map.values()), "meta": {"cached": cached}})
    return jsonify({"data": [], "meta": {"cached": cached}})

@teams_bp.route("/teams/<team_name>", methods=["GET"])
def get_team(team_name):
    year = request.args.get("year", "2024")
    sessions = openf1_client.get("/v1/sessions", params={"year": year})
    if not sessions:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Team not found", "status": 404}}), 404
        
    session_key = sessions[-1].get("session_key")
    data, cached = fetch_with_cache("drivers_for_team", "/v1/drivers", 86400, session_key=session_key)
    
    if data:
        drivers = [d for d in data if d.get("team_name", "").lower() == team_name.lower()]
        if drivers:
            team = {
                "team_name": drivers[0].get("team_name"),
                "team_colour": drivers[0].get("team_colour"),
                "drivers": drivers
            }
            return jsonify({"data": team, "meta": {"cached": cached}})
            
    return jsonify({"error": {"code": "NOT_FOUND", "message": "Team not found", "status": 404}}), 404
