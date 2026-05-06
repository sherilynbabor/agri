import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    # 🌿 CONFIGURATION
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI="sqlite:///agriyu.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, "static", "uploads")
    )

    # 🌱 INIT DB
    db.init_app(app)

    # 🌾 ENSURE UPLOAD FOLDER EXISTS
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # 🌿 IMPORT MODELS (IMPORTANT)
    from app import models

    # 🚜 REGISTER ROUTES
    from app.routes import main
    app.register_blueprint(main)

    # 🌱 CREATE DB (OK FOR DEV ONLY)
    with app.app_context():
        db.create_all()

    return app