from flask import Flask

from .config import Config
from .extensions import db
from .routes import blueprint


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set up logging
    app.logger.setLevel(app.config["LOG_LEVEL"])
    
    # Initialize the database and ORM
    db.init_app(app)

    # Set up routes
    app.register_blueprint(blueprint)

    return app