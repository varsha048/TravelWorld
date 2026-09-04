from flask import Blueprint, request, jsonify, g
from extensions import db
from models import Wishlist, Tour
from auth_utils import token_required

wishlist_bp = Blueprint("wishlist", __name__)

@wishlist_bp.route("", methods=["GET"])
@token_required
def get_wishlist():
    items = Wishlist.query.filter_by(user_id=g.current_user.id).all()
    return jsonify(status="success", data=[item.to_dict() for item in items]), 200

@wishlist_bp.route("/<int:tour_id>", methods=["POST"])
@token_required
def toggle_wishlist(tour_id):
    tour = Tour.query.get(tour_id)
    if not tour:
        return jsonify(status="fail", message="Tour not found"), 404
        
    existing = Wishlist.query.filter_by(user_id=g.current_user.id, tour_id=tour_id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify(status="success", message="Removed from wishlist", action="removed"), 200
    else:
        new_item = Wishlist(user_id=g.current_user.id, tour_id=tour_id)
        db.session.add(new_item)
        db.session.commit()
        return jsonify(status="success", message="Added to wishlist", action="added"), 201
