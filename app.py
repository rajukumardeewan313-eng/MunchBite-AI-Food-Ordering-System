"""AI-Enabled Online Food Ordering Management System - Flask entry point."""
import logging
import secrets
from datetime import datetime

from flask import Flask, abort, render_template, request, session

from config import Config
from errors import DBError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from routes import admin_routes, auth_routes, chatbot_routes, shop_routes
    for module in (shop_routes, auth_routes, chatbot_routes, admin_routes):
        app.register_blueprint(module.bp)

    @app.before_request
    def csrf_protect():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        if request.method == "POST":
            token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token") or ""
            if not secrets.compare_digest(token, session["csrf"]):
                abort(400)

    @app.context_processor
    def inject():
        return {"csrf_token": session.get("csrf", ""),
                "cart_count": sum(session.get("cart", {}).values()),
                "logged_in": bool(session.get("customer_id")),
                "customer_name": session.get("customer_name"),
                "is_admin": bool(session.get("admin_id"))}

    @app.template_filter("rs")
    def rs(v):
        return f"Rs. {float(v or 0):,.0f}"

    @app.template_filter("dt")
    def dt(v):
        return v.strftime("%d %b %Y, %H:%M") if isinstance(v, datetime) else (v if v is not None else "-")

    @app.errorhandler(DBError)
    def db_error(_):
        return render_template("error.html", code=503, message="The database is unavailable right now. "
                               "Please try again in a moment."), 503

    @app.errorhandler(400)
    def bad_request(_):
        return render_template("error.html", code=400, message="Invalid or expired request. "
                               "Go back, refresh the page and try again."), 400

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(Exception)
    def server_error(e):
        if hasattr(e, "code") and isinstance(e.code, int) and e.code < 500:
            return render_template("error.html", code=e.code, message=e.description), e.code
        logging.getLogger(__name__).exception("Unhandled error")
        return render_template("error.html", code=500, message="Something went wrong. Please try again."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, port=5000)
