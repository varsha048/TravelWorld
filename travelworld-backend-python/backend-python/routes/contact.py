from flask import Blueprint, request, jsonify

from extensions import db
from models import ContactMessage
from auth_utils import token_required, admin_required

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("", methods=["POST"])
@contact_bp.route("/", methods=["POST"])
def send_message():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify(status="fail", message="Name, email, and message are required"), 400

    db.session.add(ContactMessage(name=name, email=email, message=message))
    db.session.commit()

    return jsonify(status="success", message="Message sent successfully"), 201


@contact_bp.route("", methods=["GET"])
@contact_bp.route("/", methods=["GET"])
@token_required
@admin_required
def get_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify(status="success", data=[m.to_dict() for m in messages]), 200


import os
import smtplib
from email.message import EmailMessage

@contact_bp.route("/reply", methods=["POST"])
@token_required
@admin_required
def reply_message():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    reply_text = (data.get("replyText") or "").strip()

    if not email or not reply_text:
        return jsonify(status="fail", message="Email and reply text are required"), 400

    mail_user = os.getenv("MAIL_USERNAME")
    mail_pass = os.getenv("MAIL_PASSWORD")

    if not mail_user or not mail_pass:
        return jsonify(status="fail", message="Email credentials are not configured on the server"), 500

    try:
        msg = EmailMessage()
        msg['Subject'] = "Reply from TravelWorld Support"
        msg['From'] = mail_user
        msg['To'] = email
        msg.set_content(reply_text)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mail_user, mail_pass)
            smtp.send_message(msg)

        return jsonify(status="success", message="Reply sent successfully!"), 200
    except Exception as e:
        return jsonify(status="error", message=f"Failed to send email: {str(e)}"), 500
