import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    # 🌿 CONFIGURATION (UPDATED)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),

        # ✅ FIX: allow Render DB (fallback to SQLite)
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///agriyu.db"
        ),

        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, "static", "uploads")
    )

    # 🌱 INIT DB
    db.init_app(app)

    # 🌾 ENSURE UPLOAD FOLDER EXISTS
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # 🌿 IMPORT MODELS
    from app import models

    # 🚜 REGISTER ROUTES
    from app.routes import main
    app.register_blueprint(main)

    # ⚠️ STILL OK FOR NOW (dev)
    with app.app_context():
        db.create_all()

    return app