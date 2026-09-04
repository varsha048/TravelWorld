from flask import Blueprint, request, jsonify, g, Response
import csv
from io import StringIO
from datetime import datetime

from extensions import db
from auth_utils import token_required, admin_required
from models import NextEscape, EscapeBooking

escapes_bp = Blueprint("escapes", __name__)

@escapes_bp.route("", methods=["POST"])
@escapes_bp.route("/", methods=["POST"])
@token_required
@admin_required
def create_escape():
    data = request.get_json(force=True, silent=True) or {}
    
    required_fields = ["title", "city", "photo", "desc", "price", "startDate", "endDate"]
    for field in required_fields:
        if not data.get(field):
            return jsonify(status="fail", message=f"Missing {field}"), 400
            
    try:
        start = datetime.strptime(data["startDate"], "%Y-%m-%d").date()
        end = datetime.strptime(data["endDate"], "%Y-%m-%d").date()
        
        escape = NextEscape(
            title=data["title"],
            city=data["city"],
            photo=data["photo"],
            desc=data["desc"],
            itinerary=data.get("itinerary", ""),
            price=float(data["price"]),
            start_date=start,
            end_date=end,
            total_slots=int(data.get("totalSlots", 20)),
            booked_slots=0
        )
        db.session.add(escape)
        db.session.commit()
        return jsonify(status="success", message="Escape created", data=escape.to_dict()), 201
    except Exception as e:
        return jsonify(status="fail", message=str(e)), 400

@escapes_bp.route("/<int:escape_id>", methods=["PUT"])
@token_required
@admin_required
def update_escape(escape_id):
    escape = NextEscape.query.get(escape_id)
    if not escape:
        return jsonify(status="fail", message="Escape not found"), 404
        
    data = request.get_json(force=True, silent=True) or {}
    
    try:
        if "title" in data: escape.title = data["title"]
        if "city" in data: escape.city = data["city"]
        if "photo" in data: escape.photo = data["photo"]
        if "desc" in data: escape.desc = data["desc"]
        if "itinerary" in data: escape.itinerary = data["itinerary"]
        if "price" in data: escape.price = float(data["price"])
        if "totalSlots" in data: escape.total_slots = int(data["totalSlots"])
        
        if "startDate" in data:
            escape.start_date = datetime.strptime(data["startDate"], "%Y-%m-%d").date()
        if "endDate" in data:
            escape.end_date = datetime.strptime(data["endDate"], "%Y-%m-%d").date()
            
        db.session.commit()
        return jsonify(status="success", message="Escape updated", data=escape.to_dict()), 200
    except Exception as e:
        return jsonify(status="fail", message=str(e)), 400

@escapes_bp.route("/<int:escape_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_escape(escape_id):
    escape = NextEscape.query.get(escape_id)
    if not escape:
        return jsonify(status="fail", message="Escape not found"), 404
        
    # delete associated bookings first
    EscapeBooking.query.filter_by(escape_id=escape_id).delete()
    db.session.delete(escape)
    db.session.commit()
    
    return jsonify(status="success", message="Escape deleted"), 200

@escapes_bp.route("/bookings/<int:booking_id>", methods=["DELETE"])
@token_required
def cancel_escape_booking(booking_id):
    booking = EscapeBooking.query.get(booking_id)
    if not booking:
        return jsonify(status="fail", message="Booking not found"), 404
        
    if booking.user_id != g.current_user.id and g.current_user.role != "admin":
        return jsonify(status="fail", message="Not authorized to cancel this booking"), 403
        
    booking.escape.booked_slots -= booking.guests_count
    
    db.session.delete(booking)
    db.session.commit()
    return jsonify(status="success", message="Booking cancelled"), 200

@escapes_bp.route("/bookings/<int:booking_id>/status", methods=["PUT"])
@token_required
@admin_required
def update_escape_booking_status(booking_id):
    data = request.get_json(force=True, silent=True) or {}
    status = data.get("status")
    
    if not status:
        return jsonify(status="fail", message="Status is required"), 400
        
    booking = EscapeBooking.query.get(booking_id)
    if not booking:
        return jsonify(status="fail", message="Booking not found"), 404
        
    booking.status = status
    db.session.commit()
    
    return jsonify(status="success", message="Escape Booking status updated", data=booking.to_dict()), 200

@escapes_bp.route("/bookings/export", methods=["GET"])
@token_required
@admin_required
def export_bookings():
    bookings = EscapeBooking.query.order_by(EscapeBooking.date.desc()).all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Booking ID", "Escape Title", "Escape Dates", "Guest Name", "Guest Phone", "Slots Booked", "Booking Date"])
    
    for b in bookings:
        dates = f"{b.escape.start_date.isoformat()} to {b.escape.end_date.isoformat()}"
        cw.writerow([
            b.id,
            b.escape.title,
            dates,
            b.guest_name,
            b.guest_phone,
            b.guests_count,
            b.date.strftime("%Y-%m-%d %H:%M")
        ])
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=escape_bookings.csv"}
    )


@escapes_bp.route("", methods=["GET"])
@escapes_bp.route("/", methods=["GET"])
def get_escapes():
    escapes = NextEscape.query.order_by(NextEscape.start_date.asc()).all()
    return jsonify(status="success", data=[e.to_dict() for e in escapes]), 200

@escapes_bp.route("/<int:escape_id>/book", methods=["POST"])
@token_required
def book_escape(escape_id):
    escape = NextEscape.query.with_for_update().get(escape_id)
    if not escape:
        return jsonify(status="fail", message="Escape not found"), 404
        
    data = request.get_json(force=True, silent=True) or {}
    guest_name = data.get("guestName")
    guest_phone = data.get("guestPhone")
    slots_to_book = int(data.get("guests", 1))
    
    if not guest_name or not guest_phone:
        return jsonify(status="fail", message="Guest Name and Phone are required"), 400
    
    if escape.booked_slots + slots_to_book > escape.total_slots:
        return jsonify(status="fail", message=f"Only {escape.total_slots - escape.booked_slots} slots left!"), 400
        
    escape.booked_slots += slots_to_book
    
    booking = EscapeBooking(
        user_id=g.current_user.id,
        escape_id=escape.id,
        guest_name=guest_name,
        guest_phone=guest_phone,
        guests_count=slots_to_book
    )
    db.session.add(booking)
    db.session.commit()
    
    return jsonify(status="success", message="Successfully booked!", data=booking.to_dict()), 200
