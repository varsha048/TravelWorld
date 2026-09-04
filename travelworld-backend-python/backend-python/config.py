import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///travelworld.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRES_IN_DAYS = int(os.getenv("JWT_EXPIRES_IN_DAYS", 7))
    PORT = int(os.getenv("PORT", 5000))
