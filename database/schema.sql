-- =====================================================================
-- AI-Enabled Online Food Ordering Management System  (Oracle 12c+/23ai)
-- 9 original tables + 2 ADDITIONAL tables (SUPPORT_TICKET, ADMIN_USER)
-- Run via:  python init_db.py   (statements are separated by semicolons)
-- Reserved-word renames: date->*_date, comment->review_comment,
-- method->payment_method, status->payment_/delivery_status
-- =====================================================================

CREATE TABLE customer (
    customer_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name     VARCHAR2(100) NOT NULL,
    email         VARCHAR2(120) NOT NULL,
    phone         VARCHAR2(20),
    city          VARCHAR2(60),
    password_hash VARCHAR2(255)  NOT NULL,
    CONSTRAINT uq_customer_email UNIQUE (email),
    CONSTRAINT chk_customer_email CHECK (INSTR(email, '@') > 1)
);

CREATE TABLE restaurant (
    restaurant_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name          VARCHAR2(100) NOT NULL,
    address       VARCHAR2(200) NOT NULL,
    city          VARCHAR2(60)  NOT NULL,
    phone         VARCHAR2(20),
    status        VARCHAR2(10) DEFAULT 'Open' NOT NULL,
    CONSTRAINT chk_restaurant_status CHECK (status IN ('Open', 'Closed'))
);

CREATE TABLE category (
    category_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR2(60) NOT NULL,
    CONSTRAINT uq_category_name UNIQUE (category_name)
);

CREATE TABLE food_item (
    food_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    restaurant_id NUMBER NOT NULL,
    category_id   NUMBER NOT NULL,
    item_name     VARCHAR2(100) NOT NULL,
    description   VARCHAR2(200),
    price         NUMBER(8,2) NOT NULL,
    is_available  NUMBER(1) DEFAULT 1 NOT NULL,
    is_spicy      NUMBER(1) DEFAULT 0 NOT NULL,
    CONSTRAINT fk_food_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurant (restaurant_id),
    CONSTRAINT fk_food_category   FOREIGN KEY (category_id)   REFERENCES category (category_id),
    CONSTRAINT uq_food_per_restaurant UNIQUE (restaurant_id, item_name),
    CONSTRAINT chk_food_price CHECK (price > 0),
    CONSTRAINT chk_food_available CHECK (is_available IN (0, 1)),
    CONSTRAINT chk_food_spicy CHECK (is_spicy IN (0, 1))
);

CREATE TABLE orders (
    order_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id   NUMBER NOT NULL,
    restaurant_id NUMBER NOT NULL,
    order_date    DATE DEFAULT SYSDATE NOT NULL,
    order_status  VARCHAR2(20) DEFAULT 'Pending' NOT NULL,
    CONSTRAINT fk_orders_customer   FOREIGN KEY (customer_id)   REFERENCES customer (customer_id),
    CONSTRAINT fk_orders_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurant (restaurant_id),
    CONSTRAINT chk_order_status CHECK (order_status IN
        ('Pending','Confirmed','Preparing','Out for Delivery','Delivered','Cancelled'))
);

CREATE TABLE order_item (
    order_id   NUMBER NOT NULL,
    food_id    NUMBER NOT NULL,
    quantity   NUMBER(3) NOT NULL,
    unit_price NUMBER(8,2) NOT NULL,
    CONSTRAINT pk_order_item PRIMARY KEY (order_id, food_id),
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    CONSTRAINT fk_oi_food  FOREIGN KEY (food_id)  REFERENCES food_item (food_id),
    CONSTRAINT chk_oi_qty   CHECK (quantity > 0),
    CONSTRAINT chk_oi_price CHECK (unit_price > 0)
);

CREATE TABLE payment (
    payment_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id       NUMBER NOT NULL,
    payment_method VARCHAR2(10) NOT NULL,
    amount         NUMBER(10,2) NOT NULL,
    payment_status VARCHAR2(10) DEFAULT 'Pending' NOT NULL,
    payment_date   DATE,
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    CONSTRAINT uq_payment_order UNIQUE (order_id),
    CONSTRAINT chk_pay_method CHECK (payment_method IN ('Cash','Card','Online')),
    CONSTRAINT chk_pay_amount CHECK (amount >= 0),
    CONSTRAINT chk_pay_status CHECK (payment_status IN ('Pending','Paid','Failed','Refunded','Cancelled'))
);

CREATE TABLE delivery (
    delivery_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id         NUMBER NOT NULL,
    delivery_address VARCHAR2(250) NOT NULL,
    rider_name       VARCHAR2(80),
    delivery_status  VARCHAR2(15) DEFAULT 'Pending' NOT NULL,
    CONSTRAINT fk_delivery_order FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    CONSTRAINT uq_delivery_order UNIQUE (order_id),
    CONSTRAINT chk_delivery_status CHECK (delivery_status IN
        ('Pending','Assigned','On the Way','Delivered','Cancelled'))
);

CREATE TABLE review (
    review_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id    NUMBER NOT NULL,
    restaurant_id  NUMBER NOT NULL,
    rating         NUMBER(1) NOT NULL,
    review_comment VARCHAR2(500),
    review_date    DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_review_customer   FOREIGN KEY (customer_id)   REFERENCES customer (customer_id),
    CONSTRAINT fk_review_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurant (restaurant_id),
    CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5)
);

-- ---------------- ADDITIONAL TABLE 1: AI / customer support ----------------
CREATE TABLE support_ticket (
    ticket_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id NUMBER NOT NULL,
    order_id    NUMBER,
    issue_type  VARCHAR2(20) NOT NULL,
    description VARCHAR2(1000) NOT NULL,
    status      VARCHAR2(15) DEFAULT 'Open' NOT NULL,
    created_at  DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_ticket_customer FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
    CONSTRAINT fk_ticket_order    FOREIGN KEY (order_id)    REFERENCES orders (order_id) ON DELETE SET NULL,
    CONSTRAINT chk_ticket_type CHECK (issue_type IN
        ('Wrong Food','Missing Item','Late Delivery','Payment Issue','Food Quality','Other')),
    CONSTRAINT chk_ticket_status CHECK (status IN ('Open','In Progress','Resolved','Closed'))
);

-- ---------------- ADDITIONAL TABLE 2: admin login ----------------
CREATE TABLE admin_user (
    admin_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username      VARCHAR2(50) NOT NULL,
    password_hash VARCHAR2(255) NOT NULL,
    CONSTRAINT uq_admin_username UNIQUE (username)
);

-- ---------------- Indexes on foreign keys ----------------
CREATE INDEX idx_food_restaurant ON food_item (restaurant_id);
CREATE INDEX idx_food_category   ON food_item (category_id);
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_restaurant ON orders (restaurant_id);
CREATE INDEX idx_review_restaurant ON review (restaurant_id);
CREATE INDEX idx_ticket_customer ON support_ticket (customer_id)
