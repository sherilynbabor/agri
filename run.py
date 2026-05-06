import os
from app import create_app

# 🚀 Create app (used by Render / Gunicorn)
app = create_app()


def get_bool_env(key, default=False):
    """Helper to safely read boolean env vars"""
    return os.environ.get(key, str(default)).lower() in ("1", "true", "yes")


# ✅ ONLY run locally (Render will NOT execute this)
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = get_bool_env("FLASK_DEBUG", True)

    print("\n🚜 Starting AgriYu Farm System...")
    print(f"🌐 Host: {host}")
    print(f"🚪 Port: {port}")
    print(f"🐞 Debug: {debug}")
    print("📸 AI Scanner: Ready\n")

    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )