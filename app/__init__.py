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

    # ⚠️ FIX: avoid circular import issues (safe import order)
    with app.app_context():

        # 🌿 IMPORT MODELS FIRST
        from app import models

        # 🚜 REGISTER ROUTES
        from app.routes import main
        app.register_blueprint(main)

        # ⚠️ WARNING: only OK for dev (Render may reset DB)
        db.create_all()

    return app