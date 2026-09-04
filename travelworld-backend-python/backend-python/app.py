from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from extensions import db, limiter
from routes.auth import auth_bp
from routes.tours import tours_bp
from routes.bookings import bookings_bp
from routes.newsletter import newsletter_bp
from routes.contact import contact_bp
from routes.assistant import assistant_bp
from routes.escapes import escapes_bp
from routes.wishlist import wishlist_bp
from routes.analytics import analytics_bp
from routes.reviews import reviews_bp
from routes.payments import payments_bp


def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)
    db.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(tours_bp, url_prefix="/api/v1/tours")
    app.register_blueprint(bookings_bp, url_prefix="/api/v1/bookings")
    app.register_blueprint(newsletter_bp, url_prefix="/api/v1/newsletter")
    app.register_blueprint(contact_bp, url_prefix="/api/v1/contact")
    app.register_blueprint(assistant_bp, url_prefix="/api/v1/assistant")
    app.register_blueprint(escapes_bp, url_prefix="/api/v1/escapes")
    app.register_blueprint(wishlist_bp, url_prefix="/api/v1/wishlist")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
    app.register_blueprint(reviews_bp, url_prefix="/api/v1/reviews")
    app.register_blueprint(payments_bp, url_prefix="/api/v1/payments")
    
    from routes.upload import upload_bp
    app.register_blueprint(upload_bp, url_prefix="/api/v1/upload")
    
    from routes.ai_trip import ai_trip_bp
    app.register_blueprint(ai_trip_bp, url_prefix="/api/v1/ai-trip")

    @app.route("/")
    def index():
        return "TravelWorld API is running. Admin panel: /admin"

    @app.route("/admin")
    @app.route("/admin/")
    def admin_index():
        return send_from_directory("static/admin", "index.html")

    @app.route("/admin/<path:filename>")
    def admin_static(filename):
        return send_from_directory("static/admin", filename)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=True)
