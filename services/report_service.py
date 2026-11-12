"""Sales reports - all computed by Oracle SQL (cancelled orders excluded)."""
from db import query, query_one


def summary():
    s = query_one("""SELECT NVL(SUM(oi.quantity * oi.unit_price), 0) AS total_sales,
                            COUNT(DISTINCT o.order_id) AS order_count
                     FROM orders o JOIN order_item oi ON oi.order_id = o.order_id
                     WHERE o.order_status <> 'Cancelled'""")
    s["avg_order"] = (s["total_sales"] / s["order_count"]) if s["order_count"] else 0
    s["cancelled"] = query_one("SELECT COUNT(*) AS n FROM orders WHERE order_status = 'Cancelled'")["n"]
    s["customers"] = query_one("SELECT COUNT(*) AS n FROM customer")["n"]
    s["open_tickets"] = query_one("SELECT COUNT(*) AS n FROM support_ticket WHERE status IN ('Open','In Progress')")["n"]
    return s


def top_items(limit=5):
    return query("""SELECT f.item_name, r.name AS restaurant_name, SUM(oi.quantity) AS qty_sold,
                           SUM(oi.quantity * oi.unit_price) AS revenue
                    FROM order_item oi JOIN orders o ON o.order_id = oi.order_id
                    JOIN food_item f ON f.food_id = oi.food_id
                    JOIN restaurant r ON r.restaurant_id = f.restaurant_id
                    WHERE o.order_status <> 'Cancelled'
                    GROUP BY f.item_name, r.name ORDER BY qty_sold DESC, revenue DESC
                    FETCH FIRST :lim ROWS ONLY""", {"lim": int(limit)})


def sales_by_restaurant():
    return query("""SELECT r.name AS restaurant_name, COUNT(DISTINCT o.order_id) AS orders,
                           SUM(oi.quantity * oi.unit_price) AS sales
                    FROM orders o JOIN restaurant r ON r.restaurant_id = o.restaurant_id
                    JOIN order_item oi ON oi.order_id = o.order_id
                    WHERE o.order_status <> 'Cancelled'
                    GROUP BY r.name ORDER BY sales DESC""")


def orders_by_status():
    return query("SELECT order_status, COUNT(*) AS n FROM orders GROUP BY order_status ORDER BY n DESC")
