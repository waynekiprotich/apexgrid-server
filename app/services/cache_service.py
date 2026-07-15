import json
from datetime import datetime, timezone, timedelta
from flask import current_app
import redis
from ..models.cache import CachedRaceData
from ..extensions import db

def get_redis_client():
    redis_url = current_app.config.get("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url)
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
            
    session_key = kwargs.get("session_key", 0)
    
    cached_record = CachedRaceData.query.filter_by(session_key=session_key, resource=cache_key).first()
    if cached_record:
        # SQLite might return naive datetimes
        if cached_record.expires_at.tzinfo is None:
            cached_record.expires_at = cached_record.expires_at.replace(tzinfo=timezone.utc)
        if cached_record.expires_at > datetime.now(timezone.utc):
            return cached_record.data
        else:
            db.session.delete(cached_record)
            db.session.commit()
    
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
            
    session_key = kwargs.get("session_key", 0)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    
    cached_record = CachedRaceData.query.filter_by(session_key=session_key, resource=cache_key).first()
    if cached_record:
        cached_record.data = data
        cached_record.expires_at = expires_at
        cached_record.fetched_at = datetime.now(timezone.utc)
    else:
        cached_record = CachedRaceData(
            session_key=session_key,
            resource=cache_key,
            data=data,
            expires_at=expires_at
        )
        db.session.add(cached_record)
    
    db.session.commit()
