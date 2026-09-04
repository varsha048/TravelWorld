import re
import os
import requests

from flask import Blueprint, request, jsonify

from extensions import db
from models import Subscriber
from auth_utils import token_required, admin_required

newsletter_bp = Blueprint("newsletter", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@newsletter_bp.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email or not EMAIL_RE.match(email):
        return jsonify(status="fail", message="Please enter a valid email"), 400

    if Subscriber.query.filter_by(email=email).first():
        return jsonify(status="fail", message="This email is already subscribed"), 400

    db.session.add(Subscriber(email=email))
    db.session.commit()

    return jsonify(status="success", message="Subscribed successfully"), 201


@newsletter_bp.route("", methods=["GET"])
@newsletter_bp.route("/", methods=["GET"])
@token_required
@admin_required
def get_subscribers():
    subs = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    return jsonify(status="success", data=[s.to_dict() for s in subs]), 200


import threading
from email_service import generate_and_send_tour_package

@newsletter_bp.route("/postcard", methods=["POST"])
def postcard():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    destination = (data.get("destination") or "").strip()

    if not email or not EMAIL_RE.match(email):
        return jsonify(status="fail", message="Please enter a valid email"), 400
    if not destination:
        return jsonify(status="fail", message="Please enter a destination"), 400

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        return jsonify(status="fail", message="GEMINI_API_KEY is not configured."), 503

    # Subscribe logic
    existing = Subscriber.query.filter_by(email=email).first()
    if not existing:
        db.session.add(Subscriber(email=email))
        db.session.commit()

    # Generate Postcard
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = f"Write a short, magical 2-3 sentence postcard to the user from their future self, describing a beautiful moment they are having right now in {destination}. Start with 'Dear Future Me,'. No emojis."
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 150
            }
        }
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        
        response_data = res.json()
        postcard_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

        # Start the background thread to generate and send the detailed email
        thread = threading.Thread(target=generate_and_send_tour_package, args=(email, destination))
        thread.daemon = True
        thread.start()

        return jsonify(status="success", data={"postcard": postcard_text}), 200
    except Exception as e:
        return jsonify(status="error", message=f"Assistant error: {str(e)}"), 500
