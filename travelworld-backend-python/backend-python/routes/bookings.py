from flask import Blueprint, request, jsonify, g

from extensions import db
from models import Booking, Tour, EscapeBooking
from auth_utils import token_required, admin_required

bookings_bp = Blueprint("bookings", __name__)


@bookings_bp.route("", methods=["POST"])
@bookings_bp.route("/", methods=["POST"])
@token_required
def create_booking():
    data = request.get_json(force=True, silent=True) or {}
    tour_id = data.get("tourId")
    guest_name = (data.get("guestName") or "").strip()
    guest_phone = (data.get("guestPhone") or "").strip()
    guests_count = data.get("guests") or 1

    if not tour_id:
        return jsonify(status="fail", message="tourId is required"), 400

    tour = Tour.query.get(tour_id)
    if not tour:
        return jsonify(status="fail", message="Tour not found"), 404

    try:
        guests_count = int(guests_count)
    except (TypeError, ValueError):
        guests_count = 1

    if guests_count < 1:
        return jsonify(status="fail", message="Guests must be at least 1"), 400

    if guests_count > tour.max_group_size:
        return jsonify(
            status="fail",
            message=f"This tour allows a maximum of {tour.max_group_size} guests",
        ), 400

    import os
    from flask import current_app
    from pdf_service import generate_ticket_pdf

    total_price = tour.price * guests_count

    booking = Booking(
        user_id=g.current_user.id,
        tour_id=tour_id,
        guest_name=guest_name or g.current_user.username,
        guest_phone=guest_phone,
        guests_count=guests_count,
        total_price=total_price,
        status="confirmed"
    )
    db.session.add(booking)
    db.session.commit()

    try:
        # Generate PDF
        pdf_path = generate_ticket_pdf(booking, tour, current_app.static_folder)
        filename = os.path.basename(pdf_path)
        booking.ticket_url = f"/static/tickets/{filename}"
        db.session.commit()
    except Exception as e:
        print(f"Error generating PDF: {e}")

    return jsonify(status="success", data=booking.to_dict()), 201


@bookings_bp.route("/my", methods=["GET"])
@token_required
def get_my_bookings():
    # Regular Tour Bookings
    bookings = Booking.query.filter_by(user_id=g.current_user.id).all()
    booking_list = []
    for b in bookings:
        d = b.to_dict()
        d["booking_type"] = "tour"
        booking_list.append(d)
        
    # Escape Bookings
    escape_bookings = EscapeBooking.query.filter_by(user_id=g.current_user.id).all()
    for eb in escape_bookings:
        d = eb.to_dict()
        d["booking_type"] = "escape"
        booking_list.append(d)
        
    # Sort chronologically (newest first) based on date
    booking_list.sort(key=lambda x: x["date"], reverse=True)
    
    return jsonify(status="success", data=booking_list), 200

@bookings_bp.route("/my/<int:booking_id>", methods=["DELETE"])
@token_required
def cancel_my_booking(booking_id):
    booking_type = request.args.get("type", "tour")
    
    if booking_type == "escape":
        booking = EscapeBooking.query.filter_by(id=booking_id, user_id=g.current_user.id).first()
    else:
        booking = Booking.query.filter_by(id=booking_id, user_id=g.current_user.id).first()
        
    if not booking:
        return jsonify(status="fail", message="Booking not found or not authorized"), 404
        
    booking.status = "cancelled"
    db.session.commit()
    return jsonify(status="success", message="Booking cancelled successfully"), 200


@bookings_bp.route("", methods=["GET"])
@bookings_bp.route("/", methods=["GET"])
@token_required
@admin_required
def get_all_bookings():
    bookings = Booking.query.all()
    booking_list = []
    for b in bookings:
        d = b.to_dict()
        d["booking_type"] = "tour"
        booking_list.append(d)
        
    escape_bookings = EscapeBooking.query.all()
    for eb in escape_bookings:
        d = eb.to_dict()
        d["booking_type"] = "escape"
        booking_list.append(d)
        
    booking_list.sort(key=lambda x: x["date"], reverse=True)
    
    return jsonify(status="success", data=booking_list), 200


@bookings_bp.route("/<int:booking_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify(status="fail", message="Booking not found"), 404

    db.session.delete(booking)
    db.session.commit()
    return jsonify(status="success", message="Booking deleted"), 200

@bookings_bp.route("/<int:booking_id>/status", methods=["PUT"])
@token_required
@admin_required
def update_booking_status(booking_id):
    data = request.get_json(force=True, silent=True) or {}
    status = data.get("status")
    
    if not status:
        return jsonify(status="fail", message="Status is required"), 400
        
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify(status="fail", message="Booking not found"), 404
        
    booking.status = status
    db.session.commit()
    
    return jsonify(status="success", message="Booking status updated", data=booking.to_dict()), 200
