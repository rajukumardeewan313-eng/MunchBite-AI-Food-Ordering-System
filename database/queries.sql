-- Reference queries used by the application (all use bind variables, e.g. :email)

-- Login lookup
SELECT customer_id, full_name, password_hash FROM customer WHERE email = :email;

-- Food search with filters
SELECT f.food_id, f.item_name, f.price, r.name AS restaurant, c.category_name
FROM food_item f JOIN restaurant r ON r.restaurant_id = f.restaurant_id
JOIN category c ON c.category_id = f.category_id
WHERE f.is_available = 1 AND LOWER(f.item_name) LIKE :kw AND f.price <= :max_price
ORDER BY f.price;

-- Order status with payment and delivery
SELECT o.order_id, o.order_status, r.name, p.payment_status, d.delivery_status, d.rider_name
FROM orders o JOIN restaurant r ON r.restaurant_id = o.restaurant_id
LEFT JOIN payment p ON p.order_id = o.order_id
LEFT JOIN delivery d ON d.order_id = o.order_id
WHERE o.customer_id = :cid ORDER BY o.order_date DESC;

-- Reports
SELECT NVL(SUM(oi.quantity * oi.unit_price), 0) AS total_sales, COUNT(DISTINCT o.order_id) AS orders
FROM orders o JOIN order_item oi ON oi.order_id = o.order_id WHERE o.order_status <> 'Cancelled';

SELECT f.item_name, SUM(oi.quantity) AS qty_sold
FROM order_item oi JOIN food_item f ON f.food_id = oi.food_id
JOIN orders o ON o.order_id = oi.order_id WHERE o.order_status <> 'Cancelled'
GROUP BY f.item_name ORDER BY qty_sold DESC FETCH FIRST 5 ROWS ONLY;

SELECT r.name, SUM(oi.quantity * oi.unit_price) AS sales
FROM orders o JOIN restaurant r ON r.restaurant_id = o.restaurant_id
JOIN order_item oi ON oi.order_id = o.order_id WHERE o.order_status <> 'Cancelled'
GROUP BY r.name ORDER BY sales DESC;
