import os
import time
import requests
from flask import current_app

class OpenF1APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code_name = "OPENF1_API_ERROR"
        if status_code == 429:
            self.code_name = "RATE_LIMITED"

def get(path, params=None):
    base_url = current_app.config.get("OPENF1_BASE_URL", "https://api.openf1.org")
    url = f"{base_url}{path}"
    
    max_retries = 4
    base_delay = 1
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
                
            if response.status_code == 404:
                return []
                
            if response.status_code == 429:
                if attempt < max_retries:
                    delay = min(base_delay * (2 ** attempt), 16)
                    time.sleep(delay)
                    continue
                else:
                    raise OpenF1APIError("Too many requests to OpenF1", 429)
            
            raise OpenF1APIError(f"OpenF1 returned {response.status_code}", 502)
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                delay = min(base_delay * (2 ** attempt), 16)
                time.sleep(delay)
                continue
            raise OpenF1APIError(f"Failed to connect to OpenF1: {str(e)}", 502)

def fetch_with_cache(resource, path, ttl_seconds, **kwargs):
    from .cache_service import get as cache_get, set as cache_set
    
    # Filter out None kwargs so they don't affect cache key
    params = {k: v for k, v in kwargs.items() if v is not None}
    
    cached = cache_get(resource, **params)
    if cached:
        return cached, True
        
    data = get(path, params=params)
    
    # We pass the session_key if it exists for DB indexing
    session_key = params.pop("session_key", 0)
    cache_set(resource, data, ttl_seconds, session_key=session_key, **params)
    
    return data, False
