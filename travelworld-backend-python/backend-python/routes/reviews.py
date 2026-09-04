from flask import Blueprint, request, jsonify, g
from extensions import db
from models import Review, Tour
from auth_utils import token_required

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.route("/<int:tour_id>", methods=["POST"])
@token_required
def create_review(tour_id):
    data = request.get_json(force=True, silent=True) or {}
    rating = data.get("rating")
    review_text = data.get("reviewText")
    photo_url = data.get("photoUrl")

    if not rating or not review_text:
        return jsonify(status="fail", message="Rating and reviewText are required"), 400

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify(status="fail", message="Rating must be between 1 and 5"), 400
    except ValueError:
        return jsonify(status="fail", message="Rating must be a number"), 400

    tour = Tour.query.get(tour_id)
    if not tour:
        return jsonify(status="fail", message="Tour not found"), 404

    review = Review(
        user_id=g.current_user.id,
        tour_id=tour_id,
        rating=rating,
        review_text=review_text,
        photo_url=photo_url
    )

    db.session.add(review)
    db.session.commit()

    return jsonify(status="success", data=review.to_dict()), 201
