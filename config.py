import os


class Config:
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "258867596098")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 hours

    MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15MB per request (multiple photos)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB per individual photo
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_IMAGES_PER_VEHICLE = 12
