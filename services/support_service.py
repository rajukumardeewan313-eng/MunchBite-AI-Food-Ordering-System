"""Support tickets (additional table created for the AI support feature)."""
from db import execute, query, query_one, transaction
from errors import ServiceError

ISSUE_TYPES = ["Wrong Food", "Missing Item", "Late Delivery", "Payment Issue", "Food Quality", "Other"]
TICKET_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]


def create_ticket(customer_id, order_id, issue_type, description):
    if issue_type not in ISSUE_TYPES:
        raise ServiceError("Issue type must be one of: " + ", ".join(ISSUE_TYPES) + ".")
    description = (description or "").strip()
    if len(description) < 5:
        raise ServiceError("Please describe the problem in a few words.")
    if order_id in (None, "", 0):
        order_id = None
    else:
        try:
            order_id = int(order_id)
        except (TypeError, ValueError):
            raise ServiceError("Invalid order number.")
        if not query_one("SELECT 1 AS x FROM orders WHERE order_id = :o AND customer_id = :c",
                         {"o": order_id, "c": customer_id}):
            raise ServiceError("That order is not on your account.")
    with transaction() as cur:
        tid = cur.var(int)
        cur.execute("INSERT INTO support_ticket (customer_id, order_id, issue_type, description) "
                    "VALUES (:c, :o, :t, :d) RETURNING ticket_id INTO :tid",
                    {"c": customer_id, "o": order_id, "t": issue_type,
                     "d": description[:1000], "tid": tid})
        return int(tid.getvalue()[0])


def customer_tickets(customer_id):
    return query("""SELECT ticket_id, order_id, issue_type, description, status, created_at
                    FROM support_ticket WHERE customer_id = :cid ORDER BY created_at DESC, ticket_id DESC""",
                 {"cid": customer_id})


def list_tickets():
    return query("""SELECT t.ticket_id AS id, c.full_name, t.order_id, t.issue_type, t.description,
                    t.status, t.created_at FROM support_ticket t
                    JOIN customer c ON c.customer_id = t.customer_id
                    ORDER BY t.created_at DESC, t.ticket_id DESC""")


def set_status(ticket_id, status):
    if status not in TICKET_STATUSES:
        raise ServiceError("Invalid ticket status.")
    execute("UPDATE support_ticket SET status = :s WHERE ticket_id = :t", {"s": status, "t": ticket_id})
