import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

from config import Config
from extensions import csrf, db, login_manager
from image_service import configure_cloudinary
from models import AdminUser


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    configure_cloudinary(app)

    from routes_admin import admin_bp
    from routes_public import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(AdminUser, int(user_id))

    @app.context_processor
    def inject_globals():
        return {"whatsapp_number": app.config["WHATSAPP_NUMBER"], "current_year": datetime.utcnow().year}

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_ENV") != "production", port=5000)
