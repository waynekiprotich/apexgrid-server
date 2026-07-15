import json
from datetime import datetime, timezone, timedelta
from flask import current_app
import redis
from ..extensions import get_db

def get_redis_client():
    redis_url = current_app.config.get("REDIS_URL")
    if redis_url:
        try:
            return redis.from_url(redis_url)
        except Exception:
            return None
    return None

def get(resource, **kwargs):
    key_suffix = "_".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    cache_key = f"{resource}:{key_suffix}" if key_suffix else resource
    
    r = get_redis_client()
    if r:
        try:
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass 
            
    # Fallback to Firestore
    db = get_db()
    # document ID can't contain '/' or other bad characters, so let's sanitize
    safe_doc_id = cache_key.replace('/', '_').replace('?', '_').replace('&', '_').replace('=', '_')
    if not safe_doc_id:
        return None
        
    doc_ref = db.collection("cache").document(safe_doc_id)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        expires_at_str = data.get("expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at > datetime.now(timezone.utc):
                return data.get("data")
            else:
                doc_ref.delete()
    return None

def set(resource, data, ttl_seconds, **kwargs):
    key_suffix = "_".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    cache_key = f"{resource}:{key_suffix}" if key_suffix else resource
    
    r = get_redis_client()
    if r:
        try:
            r.setex(cache_key, ttl_seconds, json.dumps(data))
        except Exception:
            pass
            
    # Fallback to Firestore
    db = get_db()
    safe_doc_id = cache_key.replace('/', '_').replace('?', '_').replace('&', '_').replace('=', '_')
    if not safe_doc_id:
        return
        
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    doc_ref = db.collection("cache").document(safe_doc_id)
    
    doc_ref.set({
        "data": data,
        "expires_at": expires_at.isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat()
    })
