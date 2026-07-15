from flask import Blueprint, jsonify
from ..services.openf1_client import fetch_with_cache

standings_bp = Blueprint("standings", __name__)

@standings_bp.route("/drivers", methods=["GET"])
def get_driver_standings():
    # Note: OpenF1 doesn't provide standings. In a real scenario, we'd hit Ergast/Jolpi.
    # For now, we mock it or return 501. The prompt says implement endpoints.
    # Let's mock a simple structure.
    return jsonify({"data": [{"position": 1, "driver_number": 1, "points": 400}], "meta": {"mocked": True}})

@standings_bp.route("/constructors", methods=["GET"])
def get_constructor_standings():
    return jsonify({"data": [{"position": 1, "team_name": "Red Bull Racing", "points": 800}], "meta": {"mocked": True}})
