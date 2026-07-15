import pytest
from app.services.cache_service import set as cache_set, get as cache_get
from app.extensions import db

def test_cache_set_and_get(app):
    with app.app_context():
        # Set cache
        data = {"key": "value"}
        cache_set("test_resource", data, ttl_seconds=60, param1="a", param2="b")
        
        # Get cache
        cached_data = cache_get("test_resource", param1="a", param2="b")
        assert cached_data == data
        
        # Get with wrong params
        wrong_data = cache_get("test_resource", param1="c", param2="b")
        assert wrong_data is None
