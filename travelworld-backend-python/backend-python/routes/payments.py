from flask import Blueprint, request, jsonify, g
import stripe
from models import Tour, NextEscape, Booking, EscapeBooking
from extensions import db
from auth_utils import token_required
import os

payments_bp = Blueprint("payments", __name__)

# Mock test key. The user should replace this with their actual Stripe Secret Key.
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock123456789")

@payments_bp.route("/create-checkout-session", methods=["POST"])
@token_required
def create_checkout_session():
    data = request.get_json(force=True, silent=True) or {}
    
    booking_type = data.get("type") # "tour" or "escape"
    item_id = data.get("itemId")
    guest_name = data.get("guestName")
    guest_phone = data.get("guestPhone")
    guests_count = int(data.get("guests", 1))
    
    if not booking_type or not item_id:
        return jsonify(status="fail", message="Missing booking type or item ID"), 400
        
    try:
        # 1. Fetch item and validate
        if booking_type == "tour":
            item = Tour.query.get(item_id)
            if not item: return jsonify(status="fail", message="Tour not found"), 404
            total_price = (item.price * guests_count) + 10 # 10 is service charge from UI
            product_name = item.title
            
        elif booking_type == "escape":
            item = NextEscape.query.with_for_update().get(item_id)
            if not item: return jsonify(status="fail", message="Escape not found"), 404
            
            if item.booked_slots + guests_count > item.total_slots:
                return jsonify(status="fail", message="Not enough slots available"), 400
                
            total_price = item.price * guests_count
            product_name = f"Escape: {item.title}"
            
        else:
            return jsonify(status="fail", message="Invalid type"), 400

        # 2. Pre-create the booking in our DB with status "pending"
        if booking_type == "tour":
            booking = Booking(
                user_id=g.current_user.id,
                tour_id=item.id,
                guest_name=guest_name,
                guest_phone=guest_phone,
                guests_count=guests_count,
                total_price=total_price,
                status="pending"
            )
        else:
            item.booked_slots += guests_count # hold the slots
            booking = EscapeBooking(
                user_id=g.current_user.id,
                escape_id=item.id,
                guest_name=guest_name,
                guest_phone=guest_phone,
                guests_count=guests_count,
                status="pending"
            )
            
        db.session.add(booking)
        db.session.commit()

        # 3. Create Stripe Checkout Session
        # Note: If the mock key is used, Stripe API call will fail. We simulate it if needed,
        # or just try it and catch the auth error to return a mock URL.
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': product_name,
                        },
                        'unit_amount': int(total_price * 100), # Stripe expects amount in smallest currency unit (paise)
                    },
                    'quantity': 1,
                }],
                
                client_reference_id=str(booking.id),
                metadata={'type': booking_type},
                mode='payment',

                success_url=f"http://127.0.0.1:5500/travelworld/success.html?booking_id={booking.id}&type={booking_type}",
                cancel_url=f"http://127.0.0.1:5500/travelworld/cancel.html?booking_id={booking.id}&type={booking_type}",
            )
            checkout_url = session.url
            
        except stripe.error.AuthenticationError:
            # Fallback for the dummy key to allow the demo to proceed
            # In production, this exception means the key is invalid.
            print("Stripe Auth Error (Mock Key used). Proceeding with simulated redirect...")
            checkout_url = f"/success.html?booking_id={booking.id}&type={booking_type}&simulated=true"
            
        return jsonify(status="success", data={"url": checkout_url})
        
    except Exception as e:
        db.session.rollback()
        return jsonify(status="fail", message=str(e)), 500


@payments_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # For production, verify signature: stripe.Webhook.construct_event(...)
        import json
        event = json.loads(payload)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session.get('client_reference_id')
        booking_type = session.get('metadata', {}).get('type')
        
        if booking_id and booking_type:
            from pdf_service import generate_ticket_pdf
            from email_service import send_booking_email
            from flask import current_app
            
            if booking_type == 'tour':
                booking = Booking.query.get(booking_id)
                if booking:
                    booking.status = 'confirmed'
                    try:
                        tour = Tour.query.get(booking.tour_id)
                        pdf_path = generate_ticket_pdf(booking, tour, current_app.static_folder)
                        filename = os.path.basename(pdf_path)
                        booking.ticket_url = f"/static/tickets/{filename}"
                        
                        # Send email (assuming dummy SMTP is set up in env or catches exception)
                        user = booking.user
                        if user and user.email:
                            send_booking_email(user.email, user.username, tour.title, f"http://127.0.0.1:5000{booking.ticket_url}")
                    except Exception as e:
                        print("Error in post-booking hooks:", e)
            else:
                booking = EscapeBooking.query.get(booking_id)
                if booking:
                    booking.status = 'confirmed'

            db.session.commit()

    return jsonify(success=True)
