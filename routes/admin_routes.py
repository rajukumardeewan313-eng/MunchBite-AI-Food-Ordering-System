"""Admin area (separate login, separate session key, table-driven pages)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from auth_utils import admin_required
from db import execute, query
from errors import ServiceError
from services import catalog_service, customer_service, report_service, review_service, support_service
from services import order_service as orders

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            a = customer_service.authenticate_admin(request.form.get("username") or request.form.get("email"),
                                                   request.form.get("password") or request.form.get("security_key"))
            session.clear()
            session["admin_id"] = a["admin_id"]
            return redirect(url_for("admin.dashboard"))
        except ServiceError as e:
            flash(str(e), "danger")
    return redirect(url_for("auth.login", role="admin"))


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@bp.route("/")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", s=report_service.summary(),
                           top=report_service.top_items(), by_rest=report_service.sales_by_restaurant(),
                           by_status=report_service.orders_by_status())


def _opts(values):
    return [(v, v) for v in values]


def _entity(name):
    """Table definition: SQL, columns, optional add-form and per-row forms."""
    yn = [(1, "Available"), (0, "Unavailable")]
    E = {
        "customers": dict(title="Customers", rows=customer_service.list_customers,
                          cols=[("id", "ID"), ("full_name", "Name"), ("email", "Email"), ("phone", "Phone"),
                                ("city", "City")], delete=True),
        "restaurants": dict(
            title="Restaurants",
            rows=lambda: query("SELECT restaurant_id AS id, name, address, city, phone, status "
                               "FROM restaurant ORDER BY restaurant_id"),
            cols=[("id", "ID"), ("name", "Name"), ("address", "Address"), ("city", "City"),
                  ("phone", "Phone"), ("status", "Status")],
            add=[("name", "Name", "text", None), ("address", "Address", "text", None), ("city", "City", "text", None),
                 ("phone", "Phone", "text", None), ("status", "Status", "select", _opts(["Open", "Closed"]))],
            forms=[dict(action="status", label="Save", fields=[("status", "select", _opts(["Open", "Closed"]), "status")])],
            delete=True),
        "categories": dict(
            title="Categories",
            rows=lambda: query("SELECT category_id AS id, category_name FROM category ORDER BY category_name"),
            cols=[("id", "ID"), ("category_name", "Category")],
            add=[("category_name", "Category name", "text", None)], delete=True),
        "foods": dict(
            title="Food items",
            rows=lambda: query("""SELECT f.food_id AS id, f.item_name, r.name AS restaurant_name, c.category_name,
                                  f.price, f.is_available, f.is_spicy FROM food_item f
                                  JOIN restaurant r ON r.restaurant_id = f.restaurant_id
                                  JOIN category c ON c.category_id = f.category_id ORDER BY f.food_id"""),
            cols=[("id", "ID"), ("item_name", "Item"), ("restaurant_name", "Restaurant"),
                  ("category_name", "Category"), ("price", "Price (Rs.)"), ("is_available", "Available"),
                  ("is_spicy", "Spicy")],
            add=lambda: [
                ("restaurant_id", "Restaurant", "select", [(r["restaurant_id"], r["name"]) for r in catalog_service.list_restaurants()]),
                ("category_id", "Category", "select", [(c["category_id"], c["category_name"]) for c in catalog_service.list_categories()]),
                ("item_name", "Item name", "text", None), ("description", "Description", "text", None),
                ("price", "Price (Rs.)", "number", None), ("is_spicy", "Spicy?", "select", [(0, "No"), (1, "Yes")])],
            forms=[dict(action="availability", label="Update", fields=[("is_available", "select", yn, "is_available")])],
            delete=True),
        "orders": dict(
            title="Orders & delivery",
            rows=lambda: [dict(o, id=o["order_id"]) for o in orders.get_orders()],
            cols=[("id", "Order"), ("customer_name", "Customer"), ("restaurant_name", "Restaurant"),
                  ("order_date", "Placed"), ("total", "Total (Rs.)"), ("payment_status", "Payment"),
                  ("delivery_status", "Delivery"), ("rider_name", "Rider")],
            forms=[dict(action="status", label="Set status", fields=[("status", "select", _opts(orders.ORDER_STATUSES), "order_status")]),
                   dict(action="delivery", label="Update delivery",
                        fields=[("rider_name", "text", None, "rider_name"),
                                ("status", "select", _opts(orders.DELIVERY_STATUSES), "delivery_status")])]),
        "payments": dict(
            title="Payments", rows=orders.list_payments,
            cols=[("id", "ID"), ("order_id", "Order"), ("full_name", "Customer"), ("payment_method", "Method"),
                  ("amount", "Amount (Rs.)"), ("payment_status", "Status"), ("payment_date", "Date")],
            forms=[dict(action="status", label="Set status", fields=[("status", "select", _opts(orders.PAYMENT_STATUSES), "payment_status")])]),
        "reviews": dict(
            title="Reviews", rows=review_service.list_reviews,
            cols=[("id", "ID"), ("full_name", "Customer"), ("restaurant_name", "Restaurant"), ("rating", "Rating"),
                  ("review_comment", "Comment"), ("review_date", "Date")], delete=True),
        "tickets": dict(
            title="Support tickets", rows=support_service.list_tickets,
            cols=[("id", "ID"), ("full_name", "Customer"), ("order_id", "Order"), ("issue_type", "Type"),
                  ("description", "Description"), ("status", "Status"), ("created_at", "Created")],
            forms=[dict(action="status", label="Set status", fields=[("status", "select", _opts(support_service.TICKET_STATUSES), "status")])]),
    }
    if name not in E:
        abort(404)
    return E[name]


DELETE_SQL = {
    "customers": "DELETE FROM customer WHERE customer_id = :id",
    "restaurants": "DELETE FROM restaurant WHERE restaurant_id = :id",
    "categories": "DELETE FROM category WHERE category_id = :id",
    "foods": "DELETE FROM food_item WHERE food_id = :id",
    "reviews": "DELETE FROM review WHERE review_id = :id",
}


@bp.route("/<name>")
@admin_required
def entity(name):
    e = _entity(name)
    add = e["add"]() if callable(e.get("add")) else e.get("add")
    return render_template("admin/entity.html", name=name, e=e, add=add, rows=e["rows"]())


@bp.post("/<name>/add")
@admin_required
def add(name):
    f = request.form
    try:
        if name == "restaurants":
            if not f.get("name", "").strip() or not f.get("address", "").strip() or not f.get("city", "").strip():
                raise ServiceError("Name, address and city are required.")
            execute("INSERT INTO restaurant (name, address, city, phone, status) VALUES (:n, :a, :c, :p, :s)",
                    {"n": f["name"].strip(), "a": f["address"].strip(), "c": f["city"].strip(),
                     "p": f.get("phone", "").strip() or None, "s": f.get("status", "Open")})
        elif name == "categories":
            if not f.get("category_name", "").strip():
                raise ServiceError("Category name is required.")
            execute("INSERT INTO category (category_name) VALUES (:n)", {"n": f["category_name"].strip()})
        elif name == "foods":
            try:
                price = float(f.get("price"))
                rid, cid, spicy = int(f.get("restaurant_id")), int(f.get("category_id")), int(f.get("is_spicy", 0))
            except (TypeError, ValueError):
                raise ServiceError("Please fill in all fields with valid values.")
            if price <= 0 or not f.get("item_name", "").strip():
                raise ServiceError("Item name is required and price must be greater than 0.")
            execute("INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_spicy) "
                    "VALUES (:r, :c, :n, :d, :p, :s)",
                    {"r": rid, "c": cid, "n": f["item_name"].strip(), "d": f.get("description", "").strip() or None,
                     "p": price, "s": 1 if spicy else 0})
        else:
            abort(404)
        flash("Added successfully.", "success")
    except ServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.entity", name=name))


@bp.post("/<name>/<int:rid>/<action>")
@admin_required
def row_action(name, rid, action):
    f = request.form
    try:
        if action == "delete" and name in DELETE_SQL:
            execute(DELETE_SQL[name], {"id": rid})
        elif (name, action) == ("restaurants", "status") and f.get("status") in ("Open", "Closed"):
            execute("UPDATE restaurant SET status = :s WHERE restaurant_id = :id", {"s": f["status"], "id": rid})
        elif (name, action) == ("foods", "availability") and f.get("is_available") in ("0", "1"):
            execute("UPDATE food_item SET is_available = :a WHERE food_id = :id", {"a": int(f["is_available"]), "id": rid})
        elif (name, action) == ("orders", "status"):
            orders.admin_set_order_status(rid, f.get("status"))
        elif (name, action) == ("orders", "delivery"):
            orders.admin_set_delivery(rid, f.get("rider_name"), f.get("status"))
        elif (name, action) == ("payments", "status"):
            orders.admin_set_payment_status(rid, f.get("status"))
        elif (name, action) == ("tickets", "status"):
            support_service.set_status(rid, f.get("status"))
        else:
            abort(404)
        flash("Saved.", "success")
    except ServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.entity", name=name))
