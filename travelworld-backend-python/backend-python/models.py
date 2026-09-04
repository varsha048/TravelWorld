from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "_id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "avatarUrl": self.avatar_url,
        }


class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    itinerary = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, default=0)
    max_group_size = db.Column(db.Integer, default=10)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship("Review", back_populates="tour", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "_id": self.id,
            "title": self.title,
            "city": self.city,
            "photo": self.photo,
            "desc": self.desc,
            "itinerary": self.itinerary,
            "price": self.price,
            "distance": self.distance,
            "maxGroupSize": self.max_group_size,
            "featured": self.featured,
            "reviews": [r.to_dict() for r in self.reviews] if self.reviews else []
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
    tour = db.relationship("Tour", back_populates="reviews")

    def to_dict(self):
        return {
            "_id": self.id,
            "user": self.user.to_dict(),
            "tourId": self.tour_id,
            "rating": self.rating,
            "reviewText": self.review_text,
            "photoUrl": self.photo_url,
            "createdAt": self.created_at.isoformat(),
        }


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
    tour = db.relationship("Tour")

    def to_dict(self):
        return {
            "_id": self.id,
            "tour": self.tour.to_dict(),
            "createdAt": self.created_at.isoformat(),
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")
    guest_name = db.Column(db.String(120))
    guest_phone = db.Column(db.String(30))
    guests_count = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Integer, default=0)
    ticket_url = db.Column(db.String(255))

    tour = db.relationship("Tour")
    user = db.relationship("User")

    def to_dict(self):
        return {
            "_id": self.id,
            "user": self.user.to_dict(),
            "tour": self.tour.to_dict(),
            "date": self.date.isoformat(),
            "status": self.status,
            "guestName": self.guest_name,
            "guestPhone": self.guest_phone,
            "guests": self.guests_count,
            "totalPrice": self.total_price,
            "ticketUrl": self.ticket_url,
        }


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"_id": self.id, "email": self.email, "createdAt": self.created_at.isoformat()}


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "createdAt": self.created_at.isoformat(),
        }


class NextEscape(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    itinerary = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_slots = db.Column(db.Integer, default=20)
    booked_slots = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "_id": self.id,
            "title": self.title,
            "city": self.city,
            "photo": self.photo,
            "desc": self.desc,
            "itinerary": self.itinerary,
            "price": self.price,
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat(),
            "totalSlots": self.total_slots,
            "bookedSlots": self.booked_slots,
        }

class EscapeBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    escape_id = db.Column(db.Integer, db.ForeignKey("next_escape.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")
    guest_name = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(30), nullable=False)
    guests_count = db.Column(db.Integer, default=1)

    escape = db.relationship("NextEscape")
    user = db.relationship("User")

    def to_dict(self):
        return {
            "_id": self.id,
            "user": self.user.to_dict(),
            "escape": self.escape.to_dict(),
            "date": self.date.isoformat(),
            "status": self.status,
            "guestName": self.guest_name,
            "guestPhone": self.guest_phone,
            "guests": self.guests_count,
        }
