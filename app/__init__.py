import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    # 🌿 CONFIGURATION (DEPLOY SAFE)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),

        # ✅ Render-safe DB config
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

    # ⚠️ FIXED IMPORT ORDER (safer for Render)
    with app.app_context():

        # 🌿 IMPORT MODELS FIRST (avoid circular issues)
        from app import models  # noqa: F401

        # 🚜 REGISTER ROUTES
        from app.routes import main
        app.register_blueprint(main)

        # ⚠️ IMPORTANT: only for dev (safe fallback for Render free tier)
        db.create_all()

    return app