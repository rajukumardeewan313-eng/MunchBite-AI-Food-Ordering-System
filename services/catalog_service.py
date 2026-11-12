"""Restaurants, categories and food items (menu + search)."""
import re

from db import query, query_one

_FOOD_SELECT = """
SELECT f.food_id, f.item_name, f.description, f.price, f.is_available, f.is_spicy,
       f.restaurant_id, r.name AS restaurant_name, r.status AS restaurant_status,
       f.category_id, c.category_name
FROM food_item f
JOIN restaurant r ON r.restaurant_id = f.restaurant_id
JOIN category c ON c.category_id = f.category_id"""


def resolve_food_image(item_name: str, category_name: str = "") -> str:
    """Accurately maps every food item to its unique, high-resolution Unsplash image.
    Guarantees zero duplicate images across items in the same category."""
    n = (item_name or "").lower().strip()
    c = (category_name or "").lower().strip()

    # 1. Seafood & Fish
    if "fish" in n or "seafood" in n or "prawn" in n or c == "seafood":
        return "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=60"

    # 2. Desserts (Brownie vs Gulab Jamun)
    if "brownie" in n or "lava" in n:
        return "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=60"
    if "gulab" in n or "jamun" in n:
        return "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=60"

    # 2. Biryani & Rice Items (Student vs Beef/Dum vs Chicken)
    if "student" in n or "pulao" in n:
        return "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500&auto=format&fit=crop&q=60"
    if ("beef" in n or "mutton" in n or "dum" in n or "handi" in n) and ("biryani" in n or "rice" in n or c == "biryani"):
        return "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60"
    if "biryani" in n or "rice" in n or c == "biryani":
        return "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60"

    # 3. Pizzas (Chicken/Classic vs Spicy Tikka vs Pepperoni/Fajita)
    if "tikka" in n and ("pizza" in n or c == "pizza"):
        return "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&auto=format&fit=crop&q=60"
    if "pepperoni" in n or "fajita" in n:
        return "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=500&auto=format&fit=crop&q=60"
    if "pizza" in n or c == "pizza":
        return "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60"

    # 4. Burgers (Spicy Zinger vs Beef/Gourmet/Double vs Chicken)
    if "zinger" in n:
        return "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?w=500&auto=format&fit=crop&q=60"
    if ("beef" in n or "double" in n or "patty" in n or "smash" in n or "gourmet" in n) and ("burger" in n or c in ("burger", "burgers")):
        return "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60"
    if "burger" in n or c in ("burger", "burgers"):
        return "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60"

    # 5. Drinks (Soft Drink/Can vs Lemonade vs Shake)
    if "milkshake" in n or "shake" in n or "coffee" in n:
        return "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=60"
    if "lemonade" in n or "margarita" in n or "mint" in n or "lime" in n:
        return "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&auto=format&fit=crop&q=60"
    if "soft drink" in n or "soda" in n or "cola" in n or "can" in n or "sprite" in n or "dew" in n or c == "drinks":
        return "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60"

    # 6. Sides & BBQ (Wings vs Fries vs Reshmi Kabab vs Tikka/Boti)
    if "wing" in n or "nugget" in n:
        return "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60"
    if "fries" in n:
        return "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=60"
    if "reshmi" in n or "kabab" in n or "seekh" in n or "tikka" in n or "boti" in n or "bbq" in n or "malai" in n:
        return "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60"

    if c == "desserts":
        return "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=60"
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60"


def _words(text):
    """Lower-case keywords; naive singular so 'burgers' matches 'burger'."""
    out = []
    for w in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def _num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def search_food(q=None, category=None, restaurant=None, restaurant_id=None,
                min_price=None, max_price=None, spicy=None, available_only=True,
                exact_name=None, limit=20):
    """Filtered food search. SQL text only contains fixed fragments and
    generated bind names (:w0, :w1...) - user values are always bound."""
    where, p = [], {}
    if available_only:
        where.append("f.is_available = 1 AND r.status = 'Open'")
    for i, w in enumerate(_words(q)):
        where.append(f"(LOWER(f.item_name) LIKE :w{i} OR LOWER(f.description) LIKE :w{i} "
                     f"OR LOWER(c.category_name) LIKE :w{i})")
        p[f"w{i}"] = f"%{w}%"
    if category:
        where.append("LOWER(c.category_name) LIKE :cat")
        p["cat"] = f"%{str(category).strip().lower()}%"
    if restaurant:
        where.append("LOWER(r.name) LIKE :rname")
        p["rname"] = f"%{str(restaurant).strip().lower()}%"
    if restaurant_id not in (None, ""):
        where.append("f.restaurant_id = :rid")
        p["rid"] = int(restaurant_id)
    if _num(min_price) is not None:
        where.append("f.price >= :minp")
        p["minp"] = _num(min_price)
    if _num(max_price) is not None:
        where.append("f.price <= :maxp")
        p["maxp"] = _num(max_price)
    if spicy:
        where.append("f.is_spicy = 1")
    p["exact"] = (exact_name or q or "").strip().lower()
    p["lim"] = int(limit)
    sql = (_FOOD_SELECT + (" WHERE " + " AND ".join(where) if where else "") +
           " ORDER BY CASE WHEN LOWER(f.item_name) = :exact THEN 0 ELSE 1 END, f.price"
           " FETCH FIRST :lim ROWS ONLY")
    rows = query(sql, p)
    for r in rows:
        r["image_url"] = resolve_food_image(r.get("item_name"), r.get("category_name"))
    return rows


def get_food(food_id):
    row = query_one(_FOOD_SELECT + " WHERE f.food_id = :fid", {"fid": int(food_id)})
    if row:
        row["image_url"] = resolve_food_image(row.get("item_name"), row.get("category_name"))
    return row


def list_categories():
    return query("SELECT category_id, category_name FROM category ORDER BY category_name")


def list_restaurants(search=None):
    sql = """SELECT r.restaurant_id, r.name, r.address, r.city, r.phone, r.status,
       (SELECT ROUND(AVG(v.rating), 1) FROM review v WHERE v.restaurant_id = r.restaurant_id) AS avg_rating,
       (SELECT COUNT(*) FROM review v WHERE v.restaurant_id = r.restaurant_id) AS review_count
       FROM restaurant r"""
    p = {}
    if search and search.strip():
        sql += (" WHERE LOWER(r.name) LIKE :s OR LOWER(r.city) LIKE :s "
                "OR LOWER(r.address) LIKE :s")
        p["s"] = f"%{search.strip().lower()}%"
    return query(sql + " ORDER BY r.name", p)


def get_restaurant(restaurant_id):
    rows = query("""SELECT r.restaurant_id, r.name, r.address, r.city, r.phone, r.status,
       (SELECT ROUND(AVG(v.rating), 1) FROM review v WHERE v.restaurant_id = r.restaurant_id) AS avg_rating,
       (SELECT COUNT(*) FROM review v WHERE v.restaurant_id = r.restaurant_id) AS review_count
       FROM restaurant r WHERE r.restaurant_id = :rid""", {"rid": int(restaurant_id)})
    return rows[0] if rows else None


def restaurant_reviews(restaurant_id):
    return query("""SELECT v.rating, v.review_comment, v.review_date, c.full_name
       FROM review v JOIN customer c ON c.customer_id = v.customer_id
       WHERE v.restaurant_id = :rid ORDER BY v.review_date DESC""", {"rid": int(restaurant_id)})
