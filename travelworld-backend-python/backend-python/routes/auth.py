from auth_utils import token_required
from flask import Blueprint, request, jsonify, current_app

from extensions import db, limiter
from models import User
from auth_utils import generate_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per hour")
def register():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify(status="fail", message="All fields are required"), 400

    if User.query.filter_by(email=email).first():
        return jsonify(status="fail", message="Email already registered"), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(status="success", message="Registered"), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("20 per hour")
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(status="fail", message="Email and password required"), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify(status="fail", message="Invalid email or password"), 401

    token = generate_token(user.id)
    
    from flask import make_response
    response = make_response(jsonify(status="success", data=user.to_dict(), token=token))
    
    # Set HttpOnly cookie
    response.set_cookie(
        "token", 
        token, 
        httponly=True, 
        secure=False, # Set to True in production with HTTPS
        samesite="Lax",
        max_age=current_app.config["JWT_EXPIRES_IN_DAYS"] * 24 * 60 * 60
    )

    return response, 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    from flask import make_response
    response = make_response(jsonify(status="success", message="Logged out successfully"))
    response.set_cookie("token", "", expires=0, httponly=True)
    return response, 200

import os
from werkzeug.utils import secure_filename
from flask import current_app

@auth_bp.route("/avatar", methods=["POST"])
@token_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify(status="fail", message="No file provided"), 400
        
    file = request.files['avatar']
    if file.filename == '':
        return jsonify(status="fail", message="No file selected"), 400
        
    if file:
        filename = secure_filename(file.filename)
        # Create user specific filename
        ext = filename.split('.')[-1]
        unique_filename = f"avatar_{g.current_user.id}.{ext}"
        
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        
        avatar_url = f"/static/uploads/{unique_filename}"
        
        # Update user
        from models import User
        from extensions import db
        user = User.query.get(g.current_user.id)
        user.avatar_url = avatar_url
        db.session.commit()
        
        return jsonify(status="success", avatarUrl=avatar_url)
