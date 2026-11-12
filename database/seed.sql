-- Sample data (fresh schema: identity IDs start at 1, so FK values below are valid)
-- Customer passwords are set to 'password123' by init_db.py

INSERT INTO restaurant (name, address, city, phone, status) VALUES ('Spice Garden', 'Shop 4, Tariq Road', 'Karachi', '021-34567890', 'Open');
INSERT INTO restaurant (name, address, city, phone, status) VALUES ('Food Palace', '12 Clifton Block 5', 'Karachi', '021-35871234', 'Open');
INSERT INTO restaurant (name, address, city, phone, status) VALUES ('Karachi Bites', 'Plot 9, Gulshan-e-Iqbal', 'Karachi', '021-34981122', 'Open');

INSERT INTO category (category_name) VALUES ('Pizza');
INSERT INTO category (category_name) VALUES ('Burger');
INSERT INTO category (category_name) VALUES ('Biryani');
INSERT INTO category (category_name) VALUES ('Drinks');
INSERT INTO category (category_name) VALUES ('Desserts');
INSERT INTO category (category_name) VALUES ('Sides');
INSERT INTO category (category_name) VALUES ('Seafood');

INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (1, 3, 'Chicken Biryani', 'Spicy chicken biryani with raita', 450, 1, 1);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (1, 3, 'Beef Biryani', 'Spicy beef biryani with raita', 520, 1, 1);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (1, 4, 'Soft Drink', '345ml chilled soft drink', 120, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (1, 7, 'Crispy Finger Fish', 'Golden crispy fried fish fillets served with spicy tartar sauce and lemon wedges.', 650, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (1, 6, 'Chicken Seekh Kabab', 'Tender minced chicken skewers char-grilled over open coals with fresh spices and mint chutney.', 590, 1, 1);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (2, 1, 'Chicken Pizza', 'Medium pizza with grilled chicken and cheese', 950, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (2, 1, 'Spicy Chicken Tikka Pizza', 'Medium pizza with spicy chicken tikka', 1100, 1, 1);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (2, 2, 'Chicken Burger', 'Crispy chicken fillet burger', 450, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (2, 2, 'Beef Burger', 'Grilled beef patty burger', 550, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (2, 2, 'Spicy Zinger Burger', 'Hot and spicy crispy chicken zinger', 480, 1, 1);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (2, 4, 'Soft Drink', '345ml chilled soft drink', 110, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (3, 2, 'Chicken Burger', 'Classic chicken burger with mayo', 400, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (3, 3, 'Chicken Biryani', 'Spicy Karachi-style chicken biryani', 480, 0, 1);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (3, 6, 'French Fries', 'Crispy salted fries', 200, 1, 0);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (3, 6, 'Spicy Chicken Wings', 'Six hot chicken wings', 550, 1, 1);
INSERT INTO food_item (restaurant_id, category_id, item_name, description, price, is_available, is_spicy) VALUES (2, 5, 'Chocolate Brownie', 'Warm brownie with chocolate sauce', 300, 1, 0);

INSERT INTO customer (full_name, email, phone, city, password_hash) VALUES ('Ali Khan', 'ali@example.com', '0300-1112233', 'Karachi', 'PENDING');
INSERT INTO customer (full_name, email, phone, city, password_hash) VALUES ('Sara Ahmed', 'sara@example.com', '0321-4445566', 'Karachi', 'PENDING');
INSERT INTO customer (full_name, email, phone, city, password_hash) VALUES ('Bilal Hussain', 'bilal@example.com', '0333-7778899', 'Hyderabad', 'PENDING');
INSERT INTO customer (full_name, email, phone, city, password_hash) VALUES ('Ayesha Malik', 'ayesha@example.com', '0345-2223344', 'Karachi', 'PENDING');

INSERT INTO orders (customer_id, restaurant_id, order_date, order_status) VALUES (1, 1, SYSDATE - 5, 'Delivered');
INSERT INTO orders (customer_id, restaurant_id, order_date, order_status) VALUES (1, 2, SYSDATE - 1/24, 'Out for Delivery');
INSERT INTO orders (customer_id, restaurant_id, order_date, order_status) VALUES (2, 3, SYSDATE - 2/24, 'Preparing');
INSERT INTO orders (customer_id, restaurant_id, order_date, order_status) VALUES (3, 2, SYSDATE - 1/48, 'Pending');
INSERT INTO orders (customer_id, restaurant_id, order_date, order_status) VALUES (2, 1, SYSDATE - 8, 'Delivered');
INSERT INTO orders (customer_id, restaurant_id, order_date, order_status) VALUES (4, 2, SYSDATE - 3, 'Cancelled');

INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (1, 1, 2, 450);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (1, 3, 2, 120);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (2, 7, 1, 450);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (2, 9, 1, 480);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (2, 10, 2, 110);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (3, 11, 2, 400);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (3, 13, 1, 200);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (4, 5, 1, 950);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (4, 10, 1, 110);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (5, 2, 1, 520);
INSERT INTO order_item (order_id, food_id, quantity, unit_price) VALUES (6, 8, 1, 550);

INSERT INTO payment (order_id, payment_method, amount, payment_status, payment_date) VALUES (1, 'Card', 1140, 'Paid', SYSDATE - 5);
INSERT INTO payment (order_id, payment_method, amount, payment_status, payment_date) VALUES (2, 'Online', 1150, 'Paid', SYSDATE - 1/24);
INSERT INTO payment (order_id, payment_method, amount, payment_status, payment_date) VALUES (3, 'Cash', 1000, 'Pending', NULL);
INSERT INTO payment (order_id, payment_method, amount, payment_status, payment_date) VALUES (4, 'Cash', 1060, 'Pending', NULL);
INSERT INTO payment (order_id, payment_method, amount, payment_status, payment_date) VALUES (5, 'Cash', 520, 'Paid', SYSDATE - 8);
INSERT INTO payment (order_id, payment_method, amount, payment_status, payment_date) VALUES (6, 'Online', 550, 'Refunded', SYSDATE - 3);

INSERT INTO delivery (order_id, delivery_address, rider_name, delivery_status) VALUES (1, 'House 21, Block 13-D, Gulshan, Karachi', 'Imran', 'Delivered');
INSERT INTO delivery (order_id, delivery_address, rider_name, delivery_status) VALUES (2, 'House 21, Block 13-D, Gulshan, Karachi', 'Kamran', 'On the Way');
INSERT INTO delivery (order_id, delivery_address, rider_name, delivery_status) VALUES (3, 'Flat 7, Saima Arcade, North Nazimabad, Karachi', NULL, 'Pending');
INSERT INTO delivery (order_id, delivery_address, rider_name, delivery_status) VALUES (4, 'Street 5, Latifabad Unit 8, Hyderabad', NULL, 'Pending');
INSERT INTO delivery (order_id, delivery_address, rider_name, delivery_status) VALUES (5, 'Flat 7, Saima Arcade, North Nazimabad, Karachi', 'Imran', 'Delivered');
INSERT INTO delivery (order_id, delivery_address, rider_name, delivery_status) VALUES (6, 'Block B, Clifton, Karachi', NULL, 'Cancelled');

INSERT INTO review (customer_id, restaurant_id, rating, review_comment, review_date) VALUES (1, 1, 5, 'Best biryani in town, arrived hot.', SYSDATE - 4);
INSERT INTO review (customer_id, restaurant_id, rating, review_comment, review_date) VALUES (2, 1, 4, 'Tasty but a little late.', SYSDATE - 7);

INSERT INTO support_ticket (customer_id, order_id, issue_type, description, status, created_at) VALUES (4, 6, 'Payment Issue', 'Please confirm my refund for the cancelled order.', 'Resolved', SYSDATE - 2)
