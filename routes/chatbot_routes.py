from flask import Blueprint, jsonify, render_template, request, session

from auth_utils import login_required
from errors import DBError, ServiceError
from services import ai_service, customer_service

bp = Blueprint("chatbot", __name__)


@bp.route("/chatbot")
@login_required
def page():
    return render_template("chatbot.html")


@bp.post("/api/chat")
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not isinstance(message, str):
        return jsonify(error="Invalid message."), 400
    customer = customer_service.get_customer(session["customer_id"])   # identity from the session only
    if not customer:
        return jsonify(error="Account not found."), 401
    try:
        return jsonify(ai_service.chat(customer, message))
    except ServiceError as e:
        return jsonify(error=str(e)), 400
    except DBError:
        return jsonify(error="The database is unavailable right now. Please try again shortly."), 503


@bp.get("/api/chat/history")
@login_required
def history():
    return jsonify(messages=ai_service.get_history(session["customer_id"]))


@bp.post("/api/chat/reset")
@login_required
def reset():
    ai_service.reset_history(session["customer_id"])
    return jsonify(ok=True)
