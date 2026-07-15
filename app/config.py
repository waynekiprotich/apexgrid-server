import os
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    if not firebase_admin._apps:
        cred_path = os.environ.get("FIREBASE_CREDENTIALS", "firebase/serviceAccountKey.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # If deployed without the file, initialize_app uses Application Default Credentials
            firebase_admin.initialize_app()

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
