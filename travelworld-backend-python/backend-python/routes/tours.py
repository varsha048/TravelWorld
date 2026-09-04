from flask import Blueprint, request, jsonify

from extensions import db
from models import Tour
from auth_utils import token_required, admin_required

tours_bp = Blueprint("tours", __name__)


# IMPORTANT: these specific routes are registered before "/<int:id>"
@tours_bp.route("/search/getFeaturedTours", methods=["GET"])
def get_featured_tours():
    tours = Tour.query.filter_by(featured=True).limit(8).all()

    if not tours:
        tours = Tour.query.order_by(Tour.created_at.desc()).limit(8).all()

    return jsonify(status="success", data=[t.to_dict() for t in tours]), 200


@tours_bp.route("/search/getTourCount", methods=["GET"])
def get_tour_count():
    count = Tour.query.count()
    return jsonify(status="success", data=count), 200


@tours_bp.route("/search/getTourBySearch", methods=["GET"])
def get_tour_by_search():
    city = request.args.get("city", "").strip()
    distance = request.args.get("distance", type=float)
    max_group_size = request.args.get("maxGroupSize", type=float)

    query = Tour.query

    if city:
        query = query.filter(
            db.or_(
                Tour.city.ilike(f"%{city}%"),
                Tour.title.ilike(f"%{city}%"),
            )
        )
    if distance:
        query = query.filter(Tour.distance >= distance)
    if max_group_size:
        query = query.filter(Tour.max_group_size >= max_group_size)

    tours = query.all()
    return jsonify(status="success", data=[t.to_dict() for t in tours]), 200


import os
import json
import requests

@tours_bp.route("/search/magic", methods=["POST"])
def magic_search():
    data = request.get_json(force=True, silent=True) or {}
    magic_query = data.get("query", "").strip()
    
    if not magic_query:
        return jsonify(status="fail", message="Please enter a search query"), 400
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        return jsonify(status="fail", message="GEMINI_API_KEY is not configured."), 503

    all_tours = Tour.query.all()
    if not all_tours:
        return jsonify(status="success", data=[]), 200

    # Prepare tours catalog for AI
    tour_catalog = []
    for t in all_tours:
        tour_catalog.append({
            "id": t.id,
            "title": t.title,
            "city": t.city,
            "desc": t.desc,
            "price": t.price,
            "distance": t.distance,
            "maxGroupSize": t.max_group_size
        })

    prompt = f"""
    The user is looking for a tour matching this description: "{magic_query}"
    
    Here is our catalog of available tours in JSON format:
    {json.dumps(tour_catalog)}
    
    Select the top 1 to 4 tours that BEST match the user's request.
    Return ONLY a valid JSON array of objects, where each object has:
    - "id": the integer ID of the tour
    - "ai_reason": a short, punchy, 1-sentence reason why this matches their query (e.g. "Perfect for couples seeking a tropical getaway!")
    
    Do NOT include markdown formatting or any other text. Only the raw JSON array.
    """

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        
        response_data = res.json()
        raw_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        ai_matches = json.loads(raw_text.strip())
        
        matched_tours = []
        # Create a dictionary for O(1) lookups
        tour_dict = {t.id: t for t in all_tours}
        
        for match in ai_matches:
            t_id = match.get("id")
            if t_id in tour_dict:
                tour_obj = tour_dict[t_id].to_dict()
                tour_obj["ai_reason"] = match.get("ai_reason", "")
                matched_tours.append(tour_obj)
                
        return jsonify(status="success", data=matched_tours), 200
        
    except Exception as e:
        print("Magic search error:", str(e))
        # Fallback to basic search if AI fails
        return jsonify(status="success", data=[t.to_dict() for t in all_tours[:3]]), 200


@tours_bp.route("", methods=["GET"])
@tours_bp.route("/", methods=["GET"])
def get_all_tours():
    query = Tour.query
    
    min_price = request.args.get("minPrice", type=float)
    max_price = request.args.get("maxPrice", type=float)
    max_group_size = request.args.get("maxGroupSize", type=int)
    
    if min_price is not None:
        query = query.filter(Tour.price >= min_price)
    if max_price is not None:
        query = query.filter(Tour.price <= max_price)
    if max_group_size is not None:
        query = query.filter(Tour.max_group_size >= max_group_size)
        
    tours = query.order_by(Tour.created_at.desc()).all()
    return jsonify(status="success", results=len(tours), data=[t.to_dict() for t in tours]), 200


@tours_bp.route("/<int:tour_id>", methods=["GET"])
def get_tour(tour_id):
    tour = Tour.query.get(tour_id)
    if not tour:
        return jsonify(status="fail", message="Tour not found"), 404
        
    from models import Review
    reviews = Review.query.filter_by(tour_id=tour_id).order_by(Review.created_at.desc()).all()
    tour_data = tour.to_dict()
    tour_data["reviews"] = [r.to_dict() for r in reviews]
    
    return jsonify(status="success", data=tour_data), 200


@tours_bp.route("", methods=["POST"])
@tours_bp.route("/", methods=["POST"])
@token_required
@admin_required
def create_tour():
    data = request.get_json(force=True, silent=True) or {}

    try:
        tour = Tour(
            title=data["title"],
            city=data["city"],
            photo=data["photo"],
            desc=data["desc"],
            price=float(data["price"]),
            distance=float(data.get("distance", 0)),
            max_group_size=int(data.get("maxGroupSize", 10)),
            featured=bool(data.get("featured", False)),
        )
    except (KeyError, ValueError) as e:
        return jsonify(status="fail", message=f"Missing or invalid field: {e}"), 400

    db.session.add(tour)
    db.session.commit()

    return jsonify(status="success", data=tour.to_dict()), 201


@tours_bp.route("/<int:tour_id>", methods=["PUT"])
@token_required
@admin_required
def update_tour(tour_id):
    tour = Tour.query.get(tour_id)
    if not tour:
        return jsonify(status="fail", message="Tour not found"), 404

    data = request.get_json(force=True, silent=True) or {}

    for field, attr in [
        ("title", "title"), ("city", "city"), ("photo", "photo"), ("desc", "desc"),
        ("price", "price"), ("distance", "distance"), ("featured", "featured"),
    ]:
        if field in data:
            setattr(tour, attr, data[field])

    if "maxGroupSize" in data:
        tour.max_group_size = data["maxGroupSize"]

    db.session.commit()
    return jsonify(status="success", data=tour.to_dict()), 200


@tours_bp.route("/<int:tour_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_tour(tour_id):
    tour = Tour.query.get(tour_id)
    if not tour:
        return jsonify(status="fail", message="Tour not found"), 404

    db.session.delete(tour)
    db.session.commit()
    return jsonify(status="success", message="Tour deleted"), 200
