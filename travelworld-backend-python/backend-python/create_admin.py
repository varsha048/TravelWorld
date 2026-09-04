"""
Usage: python create_admin.py <email> <password> [username]
"""
import sys

from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password> [username]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    username = sys.argv[3] if len(sys.argv) > 3 else "Admin"

    user = User.query.filter_by(email=email).first()

    if user:
        user.role = "admin"
        db.session.commit()
        print(f"Existing user {email} promoted to admin")
    else:
        user = User(username=username, email=email, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user created: {email}")
