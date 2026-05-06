import os
from app import create_app

# 🚀 Create Flask app
app = create_app()


def get_bool_env(key, default=False):
    """Helper to safely read boolean env vars"""
    return os.environ.get(key, str(default)).lower() in ("1", "true", "yes")


if __name__ == "__main__":

    # 🌿 ENV CONFIG (safe + flexible)
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = get_bool_env("FLASK_DEBUG", True)

    print("\n🚜 Starting AgriYu Farm System...")
    print(f"🌐 Host: {host}")
    print(f"🚪 Port: {port}")
    print(f"🐞 Debug: {debug}")
    print("📸 AI Scanner: Ready\n")

    # 🚀 RUN APP
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        threaded=True
    )