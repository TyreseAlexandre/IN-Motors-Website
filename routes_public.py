from flask import Blueprint, abort, render_template, request

from extensions import db
from models import Vehicle

public_bp = Blueprint("public", __name__)

HOMEPAGE_VEHICLE_LIMIT = 5


@public_bp.route("/")
def index():
    vehicles = (
        Vehicle.query.filter_by(is_visible=True)
        .order_by(Vehicle.is_featured.desc(), Vehicle.created_at.desc())
        .limit(HOMEPAGE_VEHICLE_LIMIT)
        .all()
    )
    return render_template("index.html", vehicles=vehicles)


@public_bp.route("/viaturas")
def vehicles_list():
    query = Vehicle.query.filter_by(is_visible=True)

    brand = (request.args.get("marca") or "").strip()
    status = (request.args.get("estado") or "").strip()
    search = (request.args.get("q") or "").strip()
    year = request.args.get("ano", type=int)
    price_min = request.args.get("preco_min", type=int)
    price_max = request.args.get("preco_max", type=int)

    if brand:
        query = query.filter(Vehicle.brand.ilike(brand))
    if status:
        query = query.filter(Vehicle.status == status)
    if year:
        query = query.filter(Vehicle.year == year)
    if price_min is not None:
        query = query.filter(Vehicle.price >= price_min)
    if price_max is not None:
        query = query.filter(Vehicle.price <= price_max)
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Vehicle.brand.ilike(like), Vehicle.model.ilike(like)))

    vehicles = query.order_by(Vehicle.is_featured.desc(), Vehicle.created_at.desc()).all()

    brands = [
        row[0]
        for row in db.session.query(Vehicle.brand).filter_by(is_visible=True).distinct().order_by(Vehicle.brand).all()
    ]

    return render_template(
        "vehicles_list.html",
        vehicles=vehicles,
        brands=brands,
        filters={
            "marca": brand,
            "estado": status,
            "q": search,
            "ano": year or "",
            "preco_min": price_min if price_min is not None else "",
            "preco_max": price_max if price_max is not None else "",
        },
    )


@public_bp.route("/viaturas/<slug>")
def vehicle_detail(slug):
    vehicle = Vehicle.query.filter_by(slug=slug, is_visible=True).first()
    if vehicle is None:
        abort(404)
    return render_template("vehicle_detail.html", vehicle=vehicle)
