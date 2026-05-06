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

    with app.app_context():

        # 🌿 IMPORT MODELS (avoid circular import)
        from app import models  # noqa: F401

        # 🚜 REGISTER ROUTES
        from app.routes import main
        app.register_blueprint(main)

        # ⚠️ DEV ONLY (safe fallback)
        db.create_all()

    return app


# ----------------------------------------------------
# 🚨 CRITICAL FIX FOR RENDER / GUNICORN
# ----------------------------------------------------
# This exposes "app:app" for Render
app = create_app()