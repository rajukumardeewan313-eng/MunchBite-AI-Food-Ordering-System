"""Login decorators and small helpers shared by route modules."""
from functools import wraps

from flask import flash, jsonify, redirect, request, session, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("customer_id"):
            if request.path.startswith("/api/"):
                return jsonify(error="Please log in first."), 401
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        return f(*a, **kw)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("admin_id"):
            flash("Admin login required.", "warning")
            return redirect(url_for("admin.login"))
        return f(*a, **kw)
    return wrapper


def safe_next(default):
    """Only follow redirects to local paths (prevents open redirects)."""
    target = request.values.get("next", "")
    return target if target.startswith("/") and not target.startswith("//") else default
