import re
import unicodedata
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

VEHICLE_STATUSES = ("disponivel", "reservado", "vendido")
STATUS_LABELS = {
    "disponivel": "Disponível",
    "reservado": "Reservado",
    "vendido": "Vendido",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "viatura"


class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)

    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.SmallInteger, nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    mileage = db.Column(db.Integer, nullable=True)
    transmission = db.Column(db.String(50), nullable=True)
    fuel_type = db.Column(db.String(50), nullable=True)
    engine = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="disponivel")
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    images = db.relationship(
        "VehicleImage",
        backref="vehicle",
        cascade="all, delete-orphan",
        order_by="VehicleImage.sort_order",
    )

    @property
    def title(self) -> str:
        return f"{self.brand} {self.model} {self.year}"

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def primary_image(self):
        for image in self.images:
            if image.is_primary:
                return image
        return self.images[0] if self.images else None

    @property
    def price_formatted(self) -> str:
        return f"{int(self.price):,} MZN".replace(",", ".")

    @property
    def mileage_formatted(self) -> str:
        if self.mileage is None:
            return ""
        return f"{int(self.mileage):,} km".replace(",", ".")

    def whatsapp_message(self) -> str:
        return f"Olá IN Motors, gostaria de saber mais sobre o {self.title}."


class VehicleImage(db.Model):
    __tablename__ = "vehicle_images"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(
        db.Integer, db.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
