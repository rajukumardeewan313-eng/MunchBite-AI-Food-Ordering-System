# AI-Enabled Online Food Ordering Management System

University Database Systems practical (OEL) project: **Oracle Database + Python (Flask) + AI Food Assistant**.

## Problem statement
Phone/chat ordering causes mistakes; menus, payments and deliveries are not in one place; reviews and sales
reports are hard to get; customers struggle to find food and get help with orders.

## Objectives
- One centralised, normalised (3NF) Oracle database for the whole ordering workflow.
- Customer web app: register/login, browse, cart, order, pay, track delivery, review.
- Admin panel: manage data, update statuses, view reports and support tickets.
- AI chatbot that answers from **live database data** and never invents transactional facts.

## Features
Customers, restaurants, categories, food items, orders with multiple items, simulated payments (Cash/Card/Online),
delivery tracking, 1-5 reviews, search (restaurants, food, orders), SQL sales reports, support tickets,
admin dashboard, CSRF protection, hashed passwords, bind variables everywhere.

## AI chatbot capabilities
Food recommendations (spicy / type / budget), menu search, price, availability, order and delivery status,
cancellation (only when Pending/Confirmed), complaints -> `SUPPORT_TICKET`, FAQ, review guidance (1-5).
Floating chat button on every customer page plus `/chatbot`.

## Architecture
```
Browser (HTML/CSS/JS) -> Flask routes -> services (all SQL) -> python-oracledb pool -> Oracle
                            |
                            +-> ai_service -> LLM (OpenAI-compatible API) -> controlled tool functions -> services
```
The LLM can only call 11 whitelisted functions (`search_food_items`, `get_food_details`, `check_food_availability`,
`get_my_orders`, `get_order_status`, `get_delivery_status`, `cancel_order`, `create_support_ticket`,
`get_restaurant_information`, `get_faq`, `submit_review`). It never writes SQL. The logged-in `customer_id` is
injected by the server from the session; arguments the model sends for identity are ignored, so one customer
cannot read another's data. If `AI_API_KEY` is missing or the API fails, a rule-based router calls the same
functions (so the demo still works).

## Database overview
Original 9 tables: CUSTOMER, RESTAURANT, CATEGORY, FOOD_ITEM, ORDERS, ORDER_ITEM (composite PK), PAYMENT (1:1 order),
DELIVERY (1:1 order), REVIEW.
**Additional tables:** `SUPPORT_TICKET` (AI/customer support) and `ADMIN_USER` (admin login).
**Additional columns:** `CUSTOMER.password_hash`, `FOOD_ITEM.description`, `FOOD_ITEM.is_spicy`.
Columns named with Oracle reserved words were renamed (`payment_date`, `review_date`, `review_comment`, `payment_method`).
Business rules: cancel only while Pending/Confirmed; cancelling a paid order marks the payment Refunded;
one restaurant per order; reviews require a delivered order from that restaurant.

## Installation
1. Python 3.10+ and an Oracle 12c+ / 23ai Free database (identity columns and `FETCH FIRST` are used).
2. Create a user: `CREATE USER food IDENTIFIED BY food_pw QUOTA UNLIMITED ON USERS; GRANT CREATE SESSION, CREATE TABLE TO food;`
3. `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. `pip install -r requirements.txt` (python-oracledb runs in thin mode: no Oracle Client needed)
5. Copy `.env.example` to `.env` and fill in the values.
6. `python init_db.py` - **drops and recreates** the tables, loads sample data and demo passwords.
7. `python app.py` and open http://127.0.0.1:5000

## Environment variables
`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN` (e.g. `localhost:1521/FREE`, or `/XEPDB1` for XE), `SECRET_KEY`,
`AI_API_KEY`, `AI_BASE_URL` (default OpenAI; any OpenAI-compatible provider works, e.g. Groq, OpenRouter, Gemini's
OpenAI endpoint), `AI_MODEL`. Never commit `.env`.

## Demo accounts
Customers: `ali@example.com`, `sara@example.com`, `bilal@example.com`, `ayesha@example.com` - password `password123`
Admin: `/admin/login` - `admin` / `admin123` (change these for anything beyond a demo)

## Sample chatbot queries (log in as Ali)
- I want spicy chicken food under 700
- Show me burgers
- How much is chicken pizza?
- Is chicken biryani available?  (Karachi Bites' version is marked unavailable in the seed data)
- Where is my order?
- I want to cancel my order (Ali's active order is Out for Delivery, so cancellation is refused with the reason)
- I received the wrong food
- How can I place an order?
- Show me Sara's order (refused)

## Security
Bind variables for every query with user input; scrypt-hashed passwords; session auth; per-customer ownership checks in
SQL; separate admin session; CSRF token on every POST (including chat API); safe redirects; raw DB errors are logged,
never shown; chat input length limits; LLM limited to whitelisted tools.
Note: chat history is kept in server memory (resets on restart) - fine for a demo, use a table/Redis for production.

## Team and responsibilities
Raju Kumar (K25SW027): requirements, problem statement, documentation. Zafarullah (K25SW035): ERD, database design,
normalization. Nasrullah (K25SW29): Oracle SQL, tables, constraints, sample data, queries. Mohsin Ali (K25SW044):
Python application, Oracle connectivity, testing. Danish Ali (K25SW36): report writing, screenshots, presentation.

## Troubleshooting
- `DPY-6005 / 503 page`: check Oracle is running, `ORACLE_DSN` service name and credentials.
- `ORA-01950 no privileges on tablespace`: grant quota to the user.
- `ORA-00955 / ORA-02264`: re-run `python init_db.py` (it drops old tables first).
- Chatbot replies look basic: `AI_API_KEY` is not set or the API call failed - check the server log.

## Future improvements
Real payment gateway, live rider tracking and ETA, persistent chat history, image uploads for menu items,
multi-restaurant carts, role-based admin accounts, automated tests.
