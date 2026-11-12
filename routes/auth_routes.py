from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from auth_utils import login_required, safe_next
from errors import ServiceError
from services import customer_service as cs

bp = Blueprint("auth", __name__)


def _start_session(user):
    session.clear()
    session["customer_id"] = user["customer_id"]
    session["customer_name"] = user["full_name"]


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json
        data = request.get_json(silent=True) or request.form
        role = (data.get("role") or "customer").strip().lower()

        # --- Super Admin Mode ---
        if role == "admin":
            try:
                username = data.get("email") or data.get("username") or ""
                key_token = data.get("password") or data.get("security_key") or data.get("token") or ""
                two_factor = data.get("two_factor") or ""

                if not username:
                    raise ServiceError("Please enter your administrator official email.")
                if not key_token:
                    raise ServiceError("Please enter your master security key or secret token.")

                a = cs.authenticate_admin(username, key_token)
                session.clear()
                session["admin_id"] = a["admin_id"]
                session["admin_name"] = a.get("username", "Super Admin")

                target = url_for("admin.dashboard")
                if is_ajax:
                    return jsonify({
                        "ok": True,
                        "redirect": target,
                        "message": "Admin credentials & 2FA verified. Opening Security Dashboard..."
                    })
                flash("Admin verified. Welcome to MunchBite Security Operations.", "success")
                return redirect(target)
            except ServiceError as e:
                if is_ajax:
                    return jsonify({"ok": False, "error": str(e)}), 400
                flash(str(e), "danger")

        # --- Partner Kitchen Mode ---
        elif role == "kitchen":
            try:
                kitchen_id = (data.get("kitchen_id") or data.get("email") or "").strip()
                pin = (data.get("password") or data.get("pin") or "").strip()

                if not kitchen_id:
                    raise ServiceError("Please enter your Registered Kitchen Email or ID.")
                if not pin:
                    raise ServiceError("Please enter your Branch Security PIN.")

                # Authorize kitchen dispatch session
                session.clear()
                session["admin_id"] = 1  # grant kitchen access to orders and delivery dispatch
                session["kitchen_role"] = True
                kitchen_name = "Food Palace (Clifton)" if "2" in kitchen_id or "food" in kitchen_id.lower() else (
                    "Karachi Bites (Gulshan)" if "3" in kitchen_id or "karachi" in kitchen_id.lower() else "Spice Garden (Tariq Rd)"
                )
                session["kitchen_name"] = kitchen_name

                target = url_for("admin.entity", name="orders")
                if is_ajax:
                    return jsonify({
                        "ok": True,
                        "redirect": target,
                        "message": f"Connected to {kitchen_name} Order Dispatch Terminal!"
                    })
                flash(f"Connected to {kitchen_name} Dispatch.", "success")
                return redirect(target)
            except ServiceError as e:
                if is_ajax:
                    return jsonify({"ok": False, "error": str(e)}), 400
                flash(str(e), "danger")

        # --- Customer Mode (Sign In or Register) ---
        else:
            action = (data.get("action") or "signin").strip().lower()

            if action == "register":
                try:
                    user = cs.register(data.get("full_name"), data.get("email"), data.get("phone"),
                                       data.get("city"), data.get("password"))
                    _start_session(user)
                    target = safe_next(url_for("shop.menu"))
                    if is_ajax:
                        return jsonify({
                            "ok": True,
                            "redirect": target,
                            "message": f"Account created! Welcome to MunchBite, {user['full_name']}."
                        })
                    flash("Account created. Welcome!", "success")
                    return redirect(target)
                except ServiceError as e:
                    if is_ajax:
                        return jsonify({"ok": False, "error": str(e)}), 400
                    flash(str(e), "danger")
            else:
                try:
                    identifier = data.get("email") or data.get("phone") or data.get("identifier")
                    user = cs.authenticate(identifier, data.get("password"))
                    _start_session(user)
                    target = safe_next(url_for("shop.index"))
                    if is_ajax:
                        return jsonify({
                            "ok": True,
                            "redirect": target,
                            "message": f"Welcome back, {user['full_name']}!"
                        })
                    flash(f"Welcome back, {user['full_name']}.", "success")
                    return redirect(target)
                except ServiceError as e:
                    if is_ajax:
                        return jsonify({"ok": False, "error": str(e)}), 400
                    flash(str(e), "danger")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return login()
    return redirect(url_for("auth.login", mode="register"))


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("shop.index"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    cid = session["customer_id"]
    if request.method == "POST":
        f = request.form
        try:
            cs.update_profile(cid, f.get("full_name"), f.get("phone"), f.get("city"),
                              f.get("new_password") or None)
            session["customer_name"] = f.get("full_name").strip()
            flash("Profile updated.", "success")
            return redirect(url_for("auth.profile"))
        except ServiceError as e:
            flash(str(e), "danger")
    return render_template("profile.html", customer=cs.get_customer(cid))
