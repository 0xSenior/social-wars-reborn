import os
from flask import Flask

from server.infrastructure.config import TEMPLATES_DIR, ServerConfig
from server.infrastructure.persistence.save_repository import save_repository
from server.application.queries.game_config_query import config_service
from server.infrastructure.web.routes import api_blueprint, register_routes
# Ensure commands are imported and registered
import server.application.commands


def create_app(config: ServerConfig = None) -> Flask:
    if config is None:
        config = ServerConfig()

    app = Flask(__name__, template_folder=TEMPLATES_DIR)
    app.secret_key = config.secret_key or os.urandom(24)

    # Initialize domain repositories & queries
    print(" [+] Initializing persistence & save repository...")
    save_repository.initialize()

    print(" [+] Initializing game configuration service...")
    config_service.reload()

    # Register Clean Web presentation routes
    register_routes(api_blueprint, config)
    app.register_blueprint(api_blueprint)

    return app
