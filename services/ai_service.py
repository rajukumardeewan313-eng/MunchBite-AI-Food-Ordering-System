"""AI Food Assistant.

Flow: user message -> LLM decides which CONTROLLED tool to call -> tool runs a
fixed, parameterised query for the LOGGED-IN customer -> LLM words the result.

Safety rules enforced in code (not just in the prompt):
  * The LLM never sees or writes SQL; it can only call the whitelisted TOOLS.
  * customer_id always comes from the server session, never from the model.
  * If AI_API_KEY is missing or the API fails, a rule-based router calls the
    same tools, so answers still come from the database.
"""
import json
import logging
import re

import requests

from config import Config
from errors import DBError, ServiceError
from services import catalog_service as catalog
from services import order_service as orders
from services import review_service as reviews
from services import support_service as support

log = logging.getLogger(__name__)
MAX_LEN = 500
_HISTORY = {}          # customer_id -> [{"role","content"}]  (in-memory, per session user)

FAQ = {
    "ordering": "To order: open the Menu, choose items and press 'Add to cart' (one restaurant per order). "
                "Open the Cart, enter your delivery address, pick a payment method (Cash, Card or Online) "
                "and press 'Place order'. You can then follow it under My Orders.",
    "delivery": "Each order has a delivery record with your address, a rider name once one is assigned, and a "
                "status (Pending, Assigned, On the Way, Delivered, Cancelled). The system does not provide "
                "estimated delivery times.",
    "payment": "Supported payment methods: Cash, Card and Online. Card and Online payments are simulated in "
               "this system and are marked Paid immediately; Cash stays Pending until delivery.",
    "cancellation": "An order can be cancelled only while its status is Pending or Confirmed. Once it is "
                    "Preparing, Out for Delivery or Delivered it can no longer be cancelled online.",
    "refund": "If you cancel an order that was already paid, its payment is marked Refunded. Any other "
              "refund or return request is not covered by an automatic rule - I can open a support ticket "
              "so a human can review it.",
    "reviews": "After an order from a restaurant is Delivered you can rate that restaurant from 1 to 5 stars "
               "and add a comment on the Reviews page, or tell me the rating here.",
    "restaurants": "Open the Restaurants page to see addresses, phone numbers, opening status and average "
                   "ratings, or ask me about a restaurant by name.",
}
_NOT_DEFINED = ("That policy is not defined in the system. Please ask for human support - I can open a "
                "support ticket for you.")


# ---------------------------------------------------------------- tools
def _food(f):
    return {"food_id": f["food_id"], "name": f["item_name"], "restaurant": f["restaurant_name"],
            "category": f["category_name"], "price_rs": float(f["price"]),
            "spicy": bool(f["is_spicy"]), "description": f["description"],
            "available": bool(f["is_available"]) and f["restaurant_status"] == "Open",
            "restaurant_open": f["restaurant_status"] == "Open"}


def _order(o):
    return {"order_id": o["order_id"], "order_status": o["order_status"],
            "restaurant": o["restaurant_name"], "placed_at": str(o["order_date"]),
            "total_rs": float(o["total"]), "payment_method": o["payment_method"],
            "payment_status": o["payment_status"], "delivery_status": o["delivery_status"],
            "rider_name": o["rider_name"], "delivery_address": o["delivery_address"],
            "items": [{"name": i["item_name"], "qty": i["quantity"]} for i in o.get("items", [])]}


def t_search_food_items(cid, a):
    rows = catalog.search_food(q=a.get("query"), category=a.get("category"), restaurant=a.get("restaurant"),
                               min_price=a.get("min_price"), max_price=a.get("max_price"),
                               spicy=a.get("spicy"), available_only=a.get("available_only") is not False,
                               limit=10)
    return {"count": len(rows), "items": [_food(r) for r in rows]}


def t_get_food_details(cid, a):
    name = a.get("name") or ""
    rows = catalog.search_food(q=name, available_only=False, exact_name=name, limit=6)
    return {"count": len(rows), "items": [_food(r) for r in rows]} if rows else \
        {"error": "No food item matching that name was found."}


def t_check_food_availability(cid, a):
    res = t_get_food_details(cid, a)
    if "items" in res:
        res["items"] = [{"name": i["name"], "restaurant": i["restaurant"], "available": i["available"],
                         "restaurant_open": i["restaurant_open"], "price_rs": i["price_rs"]}
                        for i in res["items"]]
    return res


def t_get_my_orders(cid, a):
    rows = orders.get_orders(customer_id=cid)[:5]
    return {"count": len(rows), "orders": [_order(o) for o in rows]} if rows else \
        {"error": "You have no orders yet."}


def _pick_order(cid, order_id):
    if order_id not in (None, ""):
        try:
            return orders.get_order(int(order_id), cid)      # ownership enforced in SQL
        except (TypeError, ValueError):
            return None
    rows = orders.get_orders(customer_id=cid)
    if not rows:
        return None
    active = [o for o in rows if o["order_status"] not in ("Delivered", "Cancelled")]
    return orders.get_order((active or rows)[0]["order_id"], cid)


def t_get_order_status(cid, a):
    o = _pick_order(cid, a.get("order_id"))
    return _order(o) if o else {"error": "I couldn't find that order on your account."}


def t_get_delivery_status(cid, a):
    o = _pick_order(cid, a.get("order_id"))
    if not o:
        return {"error": "I couldn't find that order on your account."}
    return {"order_id": o["order_id"], "order_status": o["order_status"],
            "delivery_status": o["delivery_status"], "rider_name": o["rider_name"],
            "delivery_address": o["delivery_address"]}


def t_cancel_order(cid, a):
    try:
        o = orders.cancel_order(cid, a.get("order_id"))
        return {"cancelled": True, "order": _order(o)}
    except ServiceError as e:
        return {"cancelled": False, "reason": str(e)}


def t_create_support_ticket(cid, a):
    tid = support.create_ticket(cid, a.get("order_id"), a.get("issue_type"), a.get("description"))
    return {"created": True, "ticket_id": tid}


def t_get_restaurant_information(cid, a):
    rows = catalog.list_restaurants(a.get("name"))
    return {"count": len(rows), "restaurants": [
        {"restaurant_id": r["restaurant_id"], "name": r["name"], "address": r["address"], "city": r["city"],
         "phone": r["phone"], "status": r["status"],
         "average_rating": float(r["avg_rating"]) if r["avg_rating"] is not None else None,
         "review_count": r["review_count"]} for r in rows]} if rows else {"error": "No restaurant found."}


def t_get_faq(cid, a):
    return {"answer": FAQ.get((a.get("topic") or "").lower(), _NOT_DEFINED)}


def t_submit_review(cid, a):
    reviews.add_review(cid, a.get("restaurant_id"), a.get("rating"), a.get("comment"))
    return {"submitted": True}


TOOL_FUNCS = {f.__name__[2:]: f for f in (
    t_search_food_items, t_get_food_details, t_check_food_availability, t_get_my_orders,
    t_get_order_status, t_get_delivery_status, t_cancel_order, t_create_support_ticket,
    t_get_restaurant_information, t_get_faq, t_submit_review)}


def _tool(name, desc, props=None, required=()):
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": {
        "type": "object", "properties": props or {}, "required": list(required)}}}


_S, _N, _B = {"type": "string"}, {"type": "number"}, {"type": "boolean"}
TOOLS = [
    _tool("search_food_items", "Search menu items in the database. Use for recommendations and menu browsing.",
          {"query": {**_S, "description": "keywords such as 'chicken' or 'burger' (no price words)"},
           "category": _S, "restaurant": _S, "min_price": _N, "max_price": {**_N, "description": "max price in Rs."},
           "spicy": {**_B, "description": "true if the customer wants spicy food"}, "available_only": _B}),
    _tool("get_food_details", "Get price/details of a food item by name.", {"name": _S}, ["name"]),
    _tool("check_food_availability", "Check whether a food item is available right now.", {"name": _S}, ["name"]),
    _tool("get_my_orders", "List the logged-in customer's most recent orders."),
    _tool("get_order_status", "Order, payment and delivery status for the customer's order. "
          "Omit order_id for the most relevant recent order.", {"order_id": {"type": "integer"}}),
    _tool("get_delivery_status", "Delivery status and rider for the customer's order.",
          {"order_id": {"type": "integer"}}),
    _tool("cancel_order", "Cancel the customer's order if business rules allow. Only call after the customer "
          "has clearly confirmed.", {"order_id": {"type": "integer"}}, ["order_id"]),
    _tool("create_support_ticket", "Create a support ticket. Only call after you know the issue type and have "
          "a description from the customer.",
          {"order_id": {"type": "integer"},
           "issue_type": {**_S, "enum": support.ISSUE_TYPES}, "description": _S},
          ["issue_type", "description"]),
    _tool("get_restaurant_information", "Address, phone, status and rating of restaurants (optionally by name).",
          {"name": _S}),
    _tool("get_faq", "Official answer for a FAQ topic.", {"topic": {**_S, "enum": list(FAQ)}}, ["topic"]),
    _tool("submit_review", "Save a 1-5 star review for a restaurant the customer received a delivered order from.",
          {"restaurant_id": {"type": "integer"}, "rating": {"type": "integer"}, "comment": _S},
          ["restaurant_id", "rating"]),
]


def run_tool(cid, name, args):
    func = TOOL_FUNCS.get(name)
    if not func:
        return {"error": "Unknown tool."}
    try:
        return func(cid, args if isinstance(args, dict) else {})
    except ServiceError as e:
        return {"error": str(e)}


# ---------------------------------------------------------------- LLM mode
def _system_prompt(customer):
    return (
        f"You are the AI Food Assistant of an online food ordering system in Pakistan. You are talking to "
        f"{customer['full_name']}, a logged-in customer. Prices are in Pakistani Rupees (Rs.).\n"
        "RULES:\n"
        "- For ANY price, availability, menu, restaurant, order, payment or delivery fact, call a tool and use "
        "only the tool result. Never invent or guess these facts, estimated delivery times, or policies.\n"
        "- If a tool finds nothing, say: \"I couldn't find that information in the system.\"\n"
        "- You can only access THIS customer's data. If asked about another person's orders or data, refuse politely.\n"
        "- Before cancel_order, state the order and ask the customer to confirm. Cancel only after a clear yes.\n"
        "- For complaints (wrong food, missing item, late delivery...), ask which order and what happened, then "
        "create_support_ticket and give the ticket number.\n"
        "- For policies use get_faq. If a policy is not defined, say a human support agent is needed.\n"
        "- For spicy requests set spicy=true; extract food words and max_price from the message.\n"
        "- Reviews: ratings are 1 to 5 only.\n"
        "- Answer briefly in plain text (no markdown), in the customer's language style. List items with name, "
        "restaurant and price.")


def _call_llm(messages):
    r = requests.post(f"{Config.AI_BASE_URL}/chat/completions",
                      headers={"Authorization": f"Bearer {Config.AI_API_KEY}"},
                      json={"model": Config.AI_MODEL, "messages": messages, "tools": TOOLS,
                            "tool_choice": "auto", "temperature": 0.2}, timeout=40)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]


def _llm_reply(customer, message):
    cid = customer["customer_id"]
    messages = ([{"role": "system", "content": _system_prompt(customer)}]
                + _HISTORY.get(cid, [])[-10:] + [{"role": "user", "content": message}])
    for _ in range(5):
        msg = _call_llm(messages)
        calls = msg.get("tool_calls")
        if not calls:
            return (msg.get("content") or "").strip() or "I couldn't find that information in the system."
        messages.append(msg)
        for c in calls:
            try:
                args = json.loads(c["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            result = run_tool(cid, c["function"]["name"], args)
            messages.append({"role": "tool", "tool_call_id": c["id"],
                             "content": json.dumps(result, default=str)})
    return "Sorry, I couldn't complete that request. Please try rephrasing."


# ---------------------------------------------------------------- rule-based fallback
_STOP = set("""i want to a an the me show give find get some any food foods item items please can you do have has
is are was be available availability in stock price prices cost costs how much what whats of for under below
less than within max maximum budget upto up rs pkr and with my on at menu eat order something good best
recommend suggest looking need like hungry spicy hot""".split())
_OTHER = re.compile(r"\b(?!my\b)[a-z]+'s\s+(order|payment|delivery|account|profile|address)|"
                    r"\b(someone|somebody|another (person|customer)|other (person|customer))\b")


def _fmt_items(items, limit=6):
    return "\n".join(f"- {i['name']} ({i['restaurant']}) - Rs. {i['price_rs']:.0f}"
                     f"{'' if i['available'] else ' [unavailable]'}" for i in items[:limit])


def _fmt_order(o):
    rider = f", rider: {o['rider_name']}" if o["rider_name"] else ""
    return (f"Order #{o['order_id']} from {o['restaurant']}: status {o['order_status']}. "
            f"Payment: {o['payment_method']} ({o['payment_status']}). "
            f"Delivery: {o['delivery_status']}{rider}. Total Rs. {o['total_rs']:.0f}.")


def _rule_reply(customer, message):
    cid, t = customer["customer_id"], message.lower()
    nid = re.search(r"#?\b(?:order\s*(?:id|number|no\.?)?\s*#?\s*)(\d+)\b|#(\d+)", t)
    order_id = int(next(g for g in nid.groups() if g)) if nid else None

    if _OTHER.search(t):
        return "Sorry, I can only share information about your own account and orders."
    if "cancel" in t:
        o = _pick_order(cid, order_id)
        if not o:
            return "I couldn't find that order on your account."
        if o["order_status"] not in orders.CANCELLABLE:
            return (f"Order #{o['order_id']} is '{o['order_status']}', so it can no longer be cancelled "
                    "online. I can open a support ticket if you need help.")
        if re.search(r"\b(yes|confirm)\b", t):
            res = t_cancel_order(cid, {"order_id": o["order_id"]})
            return (f"Order #{o['order_id']} has been cancelled." if res["cancelled"] else res["reason"])
        return (f"Order #{o['order_id']} ({o['order_status']}) can be cancelled. "
                f"Reply 'yes, cancel order {o['order_id']}' to confirm.")
    if re.search(r"\bwrong\b|\bmissing\b|\blate\b|(was|arrived|came|is) cold|\bdamag|\bspoil|\bcomplain|"
                 r"\brefund|not received|never (came|arrived)|bad (food|quality)|problem with", t):
        kind = ("Wrong Food" if "wrong" in t else "Missing Item" if "missing" in t else
                "Late Delivery" if "late" in t else "Payment Issue" if "refund" in t else "Other")
        o = _pick_order(cid, order_id)
        res = t_create_support_ticket(cid, {"order_id": o["order_id"] if o else None,
                                            "issue_type": kind, "description": message})
        return (f"I'm sorry about that. I created support ticket #{res['ticket_id']} "
                f"({kind}{', order #' + str(o['order_id']) if o else ''}). Our team will review it.")
    if re.search(r"how (can|do) i (place|make|order)|how to order|place an order", t):
        return FAQ["ordering"]
    if re.search(r"where.*order|order status|track|my order|delivery status|status of|rider", t):
        res = t_get_order_status(cid, {"order_id": order_id})
        return res["error"] if "error" in res else _fmt_order(res)
    for topic, pat in (("payment", r"payment|\bpay\b"), ("delivery", r"deliver"),
                       ("refund", r"refund|return"), ("reviews", r"\breview|\brating|\brate\b"),
                       ("cancellation", r"cancel")):
        if re.search(pat, t) and not re.search(r"\d", t):
            return FAQ[topic]
    if re.search(r"restaurant|address|phone number|opening|open now", t):
        name = " ".join(w for w in re.findall(r"[a-z]+", t) if w not in _STOP and
                        w not in ("restaurant", "restaurants", "address", "phone", "number", "opening", "open",
                                  "now", "where", "when", "tell", "about", "information", "info", "list", "all"))
        res = t_get_restaurant_information(cid, {"name": name})
        if "error" in res:
            return "I couldn't find that information in the system."
        return "\n".join(f"- {r['name']}, {r['address']}, {r['city']} | {r['phone']} | {r['status']}"
                         f"{' | rating ' + str(r['average_rating']) if r['average_rating'] else ''}"
                         for r in res["restaurants"])

    # food intents
    m = re.search(r"(?:under|below|less than|within|upto|up to|max(?:imum)?|budget(?: of)?)\s*(?:rs\.?|pkr)?\s*(\d+)", t) \
        or re.search(r"(?:rs\.?|pkr)\s*(\d+)", t)
    max_price = float(m.group(1)) if m else None
    words = [w for w in re.findall(r"[a-z]+", t) if w not in _STOP]
    name = " ".join(words)
    if re.search(r"available|in stock", t):
        res = t_check_food_availability(cid, {"name": name})
        if "error" in res:
            return "I couldn't find that item in the system."
        return "\n".join(f"- {i['name']} at {i['restaurant']}: "
                         f"{'available' if i['available'] else 'currently NOT available'}"
                         for i in res["items"])
    if re.search(r"price|how much|cost", t):
        res = t_get_food_details(cid, {"name": name})
        if "error" in res:
            return "I couldn't find that item in the system."
        return "\n".join(f"- {i['name']} at {i['restaurant']}: Rs. {i['price_rs']:.0f}"
                         f"{'' if i['available'] else ' (currently unavailable)'}" for i in res["items"])
    res = t_search_food_items(cid, {"query": name or None, "max_price": max_price,
                                    "spicy": bool(re.search(r"spicy|hot|chatpata|teekha", t))})
    if not res["items"]:
        return "I couldn't find matching available items. Try different keywords or a higher budget."
    return "Here is what I found:\n" + _fmt_items(res["items"])


# ---------------------------------------------------------------- public API
def get_history(cid):
    return list(_HISTORY.get(cid, []))


def reset_history(cid):
    _HISTORY.pop(cid, None)


def chat(customer, message):
    """Return {"reply": str, "mode": "llm" | "rules"}. Raises ServiceError on invalid input."""
    message = (message or "").strip()
    if not message:
        raise ServiceError("Please type a message.")
    if len(message) > MAX_LEN:
        raise ServiceError(f"Message is too long (max {MAX_LEN} characters).")
    mode = "llm"
    try:
        if not Config.AI_API_KEY or Config.AI_API_KEY.startswith("your_"):
            raise RuntimeError("AI_API_KEY not configured")
        reply = _llm_reply(customer, message)
    except DBError:
        raise
    except Exception as e:     # API failure / not configured -> database-backed fallback
        log.warning("LLM unavailable (%s); using rule-based assistant", e)
        mode, reply = "rules", _rule_reply(customer, message)
    hist = _HISTORY.setdefault(customer["customer_id"], [])
    hist += [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
    del hist[:-12]
    return {"reply": reply, "mode": mode}
