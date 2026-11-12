"""Orders, order items, payments and deliveries (one transaction per order)."""
from datetime import datetime

from db import execute, query, query_one, transaction
from errors import ServiceError
from services.catalog_service import get_food

ORDER_STATUSES = ["Pending", "Confirmed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]
DELIVERY_STATUSES = ["Pending", "Assigned", "On the Way", "Delivered", "Cancelled"]
PAYMENT_STATUSES = ["Pending", "Paid", "Failed", "Refunded", "Cancelled"]
PAYMENT_METHODS = ["Cash", "Card", "Online"]
CANCELLABLE = ("Pending", "Confirmed")   # business rule: cancel only before preparation

_ORDER_SELECT = """
SELECT o.order_id, o.customer_id, o.order_date, o.order_status, o.restaurant_id,
       r.name AS restaurant_name, c.full_name AS customer_name,
       NVL((SELECT SUM(oi.quantity * oi.unit_price) FROM order_item oi
            WHERE oi.order_id = o.order_id), 0) AS total,
       p.payment_id, p.payment_method, p.payment_status, p.payment_date,
       d.delivery_address, d.rider_name, d.delivery_status
FROM orders o
JOIN restaurant r ON r.restaurant_id = o.restaurant_id
JOIN customer c ON c.customer_id = o.customer_id
LEFT JOIN payment p ON p.order_id = o.order_id
LEFT JOIN delivery d ON d.order_id = o.order_id"""


def place_order(customer_id, cart, address, method):
    """Validate the cart against the DB, then insert order + items + payment + delivery."""
    if not cart:
        raise ServiceError("Your cart is empty.")
    address = (address or "").strip()
    if len(address) < 5:
        raise ServiceError("Please enter a valid delivery address.")
    if method not in PAYMENT_METHODS:
        raise ServiceError("Please choose a valid payment method.")
    items, restaurants = [], set()
    for fid, qty in cart.items():
        try:
            fid, qty = int(fid), int(qty)
        except (TypeError, ValueError):
            raise ServiceError("Invalid cart item.")
        if not 1 <= qty <= 20:
            raise ServiceError("Quantity must be between 1 and 20.")
        food = get_food(fid)
        if not food:
            raise ServiceError(f"Food item #{fid} does not exist.")
        if not food["is_available"] or food["restaurant_status"] != "Open":
            raise ServiceError(f"{food['item_name']} is currently unavailable. Remove it to continue.")
        items.append((food, qty))
        restaurants.add(food["restaurant_id"])
    if len(restaurants) > 1:
        raise ServiceError("An order can contain items from one restaurant only.")
    total = sum(f["price"] * q for f, q in items)
    paid = method in ("Card", "Online")      # simulated payment workflow
    with transaction() as cur:
        oid = cur.var(int)
        cur.execute("INSERT INTO orders (customer_id, restaurant_id, order_status) "
                    "VALUES (:c, :r, 'Pending') RETURNING order_id INTO :oid",
                    {"c": customer_id, "r": restaurants.pop(), "oid": oid})
        order_id = int(oid.getvalue()[0])
        cur.executemany(
            "INSERT INTO order_item (order_id, food_id, quantity, unit_price) "
            "VALUES (:o, :f, :q, :u)",
            [{"o": order_id, "f": f["food_id"], "q": q, "u": f["price"]} for f, q in items])
        cur.execute("INSERT INTO payment (order_id, payment_method, amount, payment_status, payment_date) "
                    "VALUES (:o, :m, :a, :s, :d)",
                    {"o": order_id, "m": method, "a": total,
                     "s": "Paid" if paid else "Pending", "d": datetime.now() if paid else None})
        cur.execute("INSERT INTO delivery (order_id, delivery_address, delivery_status) "
                    "VALUES (:o, :a, 'Pending')", {"o": order_id, "a": address})
    return order_id


def get_orders(customer_id=None, status=None, search=None):
    where, p = [], {}
    if customer_id is not None:
        where.append("o.customer_id = :cid")
        p["cid"] = customer_id
    if status in ORDER_STATUSES:
        where.append("o.order_status = :st")
        p["st"] = status
    if search and search.strip():
        where.append("(LOWER(r.name) LIKE :s OR TO_CHAR(o.order_id) = :raw)")
        p["s"] = f"%{search.strip().lower()}%"
        p["raw"] = search.strip()
    sql = _ORDER_SELECT + (" WHERE " + " AND ".join(where) if where else "")
    return query(sql + " ORDER BY o.order_date DESC, o.order_id DESC", p)


def get_order(order_id, customer_id=None):
    """Return one order with its items. If customer_id is given the order must
    belong to that customer (ownership check)."""
    sql, p = _ORDER_SELECT + " WHERE o.order_id = :oid", {"oid": int(order_id)}
    if customer_id is not None:
        sql += " AND o.customer_id = :cid"
        p["cid"] = customer_id
    order = query_one(sql, p)
    if order:
        order["items"] = query(
            """SELECT f.item_name, oi.quantity, oi.unit_price, oi.quantity * oi.unit_price AS line_total
               FROM order_item oi JOIN food_item f ON f.food_id = oi.food_id
               WHERE oi.order_id = :oid ORDER BY f.item_name""", {"oid": int(order_id)})
    return order


def cancel_order(customer_id, order_id):
    order = get_order(order_id, customer_id)
    if not order:
        raise ServiceError("I couldn't find that order on your account.")
    if order["order_status"] not in CANCELLABLE:
        raise ServiceError(f"Order #{order['order_id']} is '{order['order_status']}' and can no "
                           "longer be cancelled online. Please contact support.")
    with transaction() as cur:
        cur.execute("UPDATE orders SET order_status = 'Cancelled' WHERE order_id = :o "
                    "AND order_status IN ('Pending', 'Confirmed')", {"o": order["order_id"]})
        if cur.rowcount == 0:
            raise ServiceError("This order can no longer be cancelled.")
        cur.execute("UPDATE delivery SET delivery_status = 'Cancelled' WHERE order_id = :o",
                    {"o": order["order_id"]})
        cur.execute("UPDATE payment SET payment_status = "
                    "CASE payment_status WHEN 'Paid' THEN 'Refunded' ELSE 'Cancelled' END "
                    "WHERE order_id = :o", {"o": order["order_id"]})
    return get_order(order_id, customer_id)


# ---------------- admin operations ----------------
def admin_set_order_status(order_id, status):
    if status not in ORDER_STATUSES:
        raise ServiceError("Invalid order status.")
    with transaction() as cur:
        cur.execute("UPDATE orders SET order_status = :s WHERE order_id = :o",
                    {"s": status, "o": order_id})
        if status == "Delivered":
            cur.execute("UPDATE delivery SET delivery_status = 'Delivered' WHERE order_id = :o", {"o": order_id})
            cur.execute("UPDATE payment SET payment_status = 'Paid', payment_date = NVL(payment_date, SYSDATE) "
                        "WHERE order_id = :o AND payment_status = 'Pending'", {"o": order_id})
        elif status == "Cancelled":
            cur.execute("UPDATE delivery SET delivery_status = 'Cancelled' WHERE order_id = :o", {"o": order_id})
            cur.execute("UPDATE payment SET payment_status = CASE payment_status WHEN 'Paid' THEN 'Refunded' "
                        "ELSE 'Cancelled' END WHERE order_id = :o", {"o": order_id})


def admin_set_delivery(order_id, rider_name, status):
    if status not in DELIVERY_STATUSES:
        raise ServiceError("Invalid delivery status.")
    execute("UPDATE delivery SET rider_name = :r, delivery_status = :s WHERE order_id = :o",
            {"r": (rider_name or "").strip() or None, "s": status, "o": order_id})


def admin_set_payment_status(payment_id, status):
    if status not in PAYMENT_STATUSES:
        raise ServiceError("Invalid payment status.")
    execute("UPDATE payment SET payment_status = :s, "
            "payment_date = CASE WHEN :s2 = 'Paid' THEN NVL(payment_date, SYSDATE) ELSE payment_date END "
            "WHERE payment_id = :p", {"s": status, "s2": status, "p": payment_id})


def list_payments():
    return query("""SELECT p.payment_id AS id, p.order_id, c.full_name, p.payment_method, p.amount,
                    p.payment_status, p.payment_date
                    FROM payment p JOIN orders o ON o.order_id = p.order_id
                    JOIN customer c ON c.customer_id = o.customer_id ORDER BY p.payment_id DESC""")
