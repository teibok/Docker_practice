import os 
from dotenv import load_dotenv
from flask import Flask

from .config import Config

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, 'static', 'uploads')
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB per request

    from .routes import user_route
    app.register_blueprint(user_route)
    return app
