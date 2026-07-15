from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://" # Defaulting to memory if redis fails, but will override in app factory
)

def init_rate_limiter(app):
    redis_url = app.config.get("REDIS_URL")
    if redis_url:
        # We need to configure it via config since Limiter already instantiated
        app.config["RATELIMIT_STORAGE_URL"] = redis_url
    limiter.init_app(app)
