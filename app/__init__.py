from flask import Flask
from .config import config, initialize_firebase
from .extensions import cors, ma

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize Firebase
    initialize_firebase()

    # Initialize extensions
    # Use a regex to allow all origins dynamically to bypass any misconfiguration in environment variables
    allowed_origins = r".*"
    cors.init_app(app, origins=allowed_origins, supports_credentials=True)
    ma.init_app(app)

    # Initialize Logger
    from .utils.logger import setup_logger
    setup_logger(app)

    # Initialize Rate Limiter
    from .middleware.rate_limit import init_rate_limiter
    init_rate_limiter(app)

    # Initialize Security Headers
    from .middleware.security import apply_security_headers
    apply_security_headers(app)

    # Register blueprints
    from .routes.health import health_bp
    from .routes.auth import auth_bp
    from .routes.drivers import drivers_bp
    from .routes.teams import teams_bp
    from .routes.standings import standings_bp
    from .routes.sessions import sessions_bp
    from .routes.telemetry import telemetry_bp
    from .routes.favorites import favorites_bp
    from .routes.dashboards import dashboards_bp
    from .routes.uploads import uploads_bp

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(drivers_bp, url_prefix="/api/v1")
    app.register_blueprint(teams_bp, url_prefix="/api/v1")
    app.register_blueprint(standings_bp, url_prefix="/api/v1/standings")
    app.register_blueprint(sessions_bp, url_prefix="/api/v1")
    app.register_blueprint(telemetry_bp, url_prefix="/api/v1")
    app.register_blueprint(favorites_bp, url_prefix="/api/v1/favorites")
    app.register_blueprint(dashboards_bp, url_prefix="/api/v1/dashboards")
    app.register_blueprint(uploads_bp, url_prefix="/api/v1/uploads")

    # Register error handlers
    from .middleware.error_handlers import register_error_handlers
    register_error_handlers(app)

    @app.route("/", methods=["GET"])
    def index():
        from flask import jsonify
        return jsonify({
            "name": "ApexGrid API",
            "status": "running",
            "version": "v1"
        })

    return app
