import os
from datetime import timedelta

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get("JWT_ACCESS_TTL", 900)))
    OPENF1_BASE_URL = os.environ.get("OPENF1_BASE_URL", "https://api.openf1.org")
    CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*").split(",")
    REDIS_URL = os.environ.get("REDIS_URL")

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

class StagingConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False

config = {
    "development": DevConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevConfig
}
