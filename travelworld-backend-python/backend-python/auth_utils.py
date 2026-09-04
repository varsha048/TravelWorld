from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request, jsonify, current_app, g

from models import User


def generate_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=current_app.config["JWT_EXPIRES_IN_DAYS"]),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("token")
        
        # Fallback to Authorization header if no cookie
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify(status="fail", message="Not logged in"), 401

        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            user = User.query.get(int(payload["sub"]))
            if not user:
                raise ValueError("User no longer exists")
            g.current_user = user
        except Exception:
            return jsonify(status="fail", message="Invalid or expired token"), 401

        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if getattr(g, 'current_user', None) is None or g.current_user.role != "admin":
            return jsonify(status="fail", message="Not authorized for this action"), 403
        return f(*args, **kwargs)

    return wrapper
