import json
import os
import requests

from flask import Blueprint, request, jsonify

from models import Tour

assistant_bp = Blueprint("assistant", __name__)

MODEL = "gemini-2.5-flash"


def build_system_prompt():
    tours = Tour.query.all()

    catalog_lines = [
        f"- id={t.id} | {t.title} | {t.city} | ${t.price} | max group {t.max_group_size} | {t.desc}"
        for t in tours
    ]
    catalog_text = "\n".join(catalog_lines) if catalog_lines else "No tours are currently available."

    return f"""You are TravelWorld's friendly travel assistant. Your job is to help website \
visitors find the right tour based on what they're looking for (destination type, budget, \
group size, activity level, etc.).

Only recommend tours from this exact catalog — never invent tours, prices, or destinations \
that aren't listed here:

{catalog_text}

Ask a brief clarifying question if the visitor's request is too vague to match anything \
confidently. Otherwise recommend 1-3 tours that best fit what they described.

Respond with ONLY valid JSON (no markdown fences, no extra text) in this exact shape:
{{"reply": "<a short, friendly, conversational response, 2-4 sentences>", "tour_ids": [<ids of recommended tours, best match first, empty array if none fit>]}}
"""


def to_gemini_role(role):
    return "model" if role == "assistant" else "user"


@assistant_bp.route("/chat", methods=["POST"])
def chat():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_key_here":
        return jsonify(
            status="fail",
            message="The AI assistant isn't configured yet. Add GEMINI_API_KEY to your .env file.",
        ), 503

    data = request.get_json(force=True, silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []  # [{role: "user"|"assistant", content: "..."}]

    if not user_message:
        return jsonify(status="fail", message="Message is required"), 400

    # Keep only the last few turns to control cost/context size
    trimmed_history = history[-8:]

    contents = [
        {"role": to_gemini_role(turn.get("role")), "parts": [{"text": turn.get("content", "")}]}
        for turn in trimmed_history
    ]
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": build_system_prompt()}]},
            "generationConfig": {
                "maxOutputTokens": 500,
                "temperature": 0.4,
                "responseMimeType": "application/json"
            }
        }
        
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        
        response_data = res.json()
        raw_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

        try:
            parsed = json.loads(raw_text)
            reply = parsed.get("reply", "")
            tour_ids = parsed.get("tour_ids", [])
        except (json.JSONDecodeError, AttributeError):
            # Fall back gracefully if the model didn't return clean JSON
            reply = raw_text
            tour_ids = []

        recommended_tours = []
        if tour_ids:
            tours = Tour.query.filter(Tour.id.in_(tour_ids)).all()
            tours_by_id = {t.id: t for t in tours}
            recommended_tours = [
                tours_by_id[tid].to_dict() for tid in tour_ids if tid in tours_by_id
            ]

        return jsonify(status="success", data={"reply": reply, "tours": recommended_tours}), 200

    except Exception as e:
        return jsonify(status="error", message=f"Assistant error: {str(e)}"), 500
