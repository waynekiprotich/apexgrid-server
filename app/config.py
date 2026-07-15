import os
import json
import logging
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            # 1. Try to load from environment variable JSON string (Render/Production)
            cred_json_str = os.environ.get("FIREBASE_CREDENTIALS")
            if cred_json_str:
                try:
                    cred_dict = json.loads(cred_json_str)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized successfully using FIREBASE_CREDENTIALS environment variable.")
                    return
                except json.JSONDecodeError:
                    logger.error("FIREBASE_CREDENTIALS environment variable contains invalid JSON.")
                    raise
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase with FIREBASE_CREDENTIALS: {e}")
                    raise

            # 2. Try to load from local file (Local Development)
            local_cred_path = "firebase/serviceAccountKey.json"
            if os.path.exists(local_cred_path):
                cred = credentials.Certificate(local_cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully using local serviceAccountKey.json.")
                return

            # 3. Fallback to Application Default Credentials (e.g. GCP, AWS)
            logger.info("Initializing Firebase with Application Default Credentials.")
            firebase_admin.initialize_app()
            
        except Exception as e:
            logger.error("Failed to initialize Firebase Admin SDK. Backend cannot start correctly.")
            raise

class BaseConfig:
    OPENF1_BASE_URL = os.environ.get("OPENF1_BASE_URL", "https://api.openf1.org")
    CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*").split(",")
    REDIS_URL = os.environ.get("REDIS_URL")
    
class DevConfig(BaseConfig):
    DEBUG = True

class StagingConfig(BaseConfig):
    DEBUG = False

class ProductionConfig(BaseConfig):
    DEBUG = False

class TestingConfig(BaseConfig):
    TESTING = True
    RATELIMIT_ENABLED = False

config = {
    "development": DevConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevConfig
}
