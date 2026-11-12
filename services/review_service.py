"""Reviews: 1-5 rating (also enforced by a CHECK constraint)."""
from db import execute, query, query_one
from errors import ServiceError


def eligible_restaurants(customer_id):
    """Restaurants the customer has received a delivered order from."""
    return query("""SELECT DISTINCT r.restaurant_id, r.name FROM orders o
                    JOIN restaurant r ON r.restaurant_id = o.restaurant_id
                    WHERE o.customer_id = :cid AND o.order_status = 'Delivered'
                    ORDER BY r.name""", {"cid": customer_id})


def add_review(customer_id, restaurant_id, rating, comment):
    try:
        rating, restaurant_id = int(rating), int(restaurant_id)
    except (TypeError, ValueError):
        raise ServiceError("Please choose a restaurant and a rating from 1 to 5.")
    if not 1 <= rating <= 5:
        raise ServiceError("Rating must be between 1 and 5.")
    comment = (comment or "").strip()[:500] or None
    if not query_one("""SELECT 1 AS x FROM orders WHERE customer_id = :cid AND restaurant_id = :rid
                        AND order_status = 'Delivered' FETCH FIRST 1 ROWS ONLY""",
                     {"cid": customer_id, "rid": restaurant_id}):
        raise ServiceError("You can review a restaurant after one of your orders from it is delivered.")
    execute("INSERT INTO review (customer_id, restaurant_id, rating, review_comment) "
            "VALUES (:c, :r, :g, :t)", {"c": customer_id, "r": restaurant_id, "g": rating, "t": comment})


def customer_reviews(customer_id):
    return query("""SELECT v.review_id, r.name AS restaurant_name, v.rating, v.review_comment, v.review_date
                    FROM review v JOIN restaurant r ON r.restaurant_id = v.restaurant_id
                    WHERE v.customer_id = :cid ORDER BY v.review_date DESC""", {"cid": customer_id})


def list_reviews():
    return query("""SELECT v.review_id AS id, c.full_name, r.name AS restaurant_name, v.rating,
                    v.review_comment, v.review_date FROM review v
                    JOIN customer c ON c.customer_id = v.customer_id
                    JOIN restaurant r ON r.restaurant_id = v.restaurant_id
                    ORDER BY v.review_date DESC""")
