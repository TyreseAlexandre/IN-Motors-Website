from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from forms import ActionForm, DeleteImageForm, LoginForm, VehicleForm
from image_service import delete_vehicle_image, upload_vehicle_image, validate_image
from models import VEHICLE_STATUSES, AdminUser, Vehicle, VehicleImage, slugify

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def unique_slug(base_text: str, exclude_id: int | None = None) -> str:
    base = slugify(base_text)
    slug = base
    suffix = 2
    while True:
        query = Vehicle.query.filter_by(slug=slug)
        if exclude_id is not None:
            query = query.filter(Vehicle.id != exclude_id)
        if query.first() is None:
            return slug
        slug = f"{base}-{suffix}"
        suffix += 1


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=False)
            next_url = request.args.get("next")
            if not next_url or not next_url.startswith("/admin"):
                next_url = url_for("admin.dashboard")
            return redirect(next_url)
        flash("Email ou palavra-passe incorretos.", "error")

    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).all()
    counts = {
        "total": len(vehicles),
        "disponivel": sum(1 for v in vehicles if v.status == "disponivel"),
        "reservado": sum(1 for v in vehicles if v.status == "reservado"),
        "vendido": sum(1 for v in vehicles if v.status == "vendido"),
    }
    action_form = ActionForm()
    return render_template("admin/dashboard.html", vehicles=vehicles, counts=counts, action_form=action_form)


def _apply_form_to_vehicle(form: VehicleForm, vehicle: Vehicle) -> None:
    vehicle.brand = form.brand.data.strip()
    vehicle.model = form.model.data.strip()
    vehicle.year = form.year.data
    vehicle.price = form.price.data
    vehicle.mileage = form.mileage.data
    vehicle.transmission = form.transmission.data or None
    vehicle.fuel_type = form.fuel_type.data or None
    vehicle.engine = (form.engine.data or "").strip() or None
    vehicle.color = (form.color.data or "").strip() or None
    vehicle.location = (form.location.data or "").strip() or None
    vehicle.description = (form.description.data or "").strip() or None
    vehicle.status = form.status.data
    vehicle.is_featured = form.is_featured.data
    vehicle.is_visible = form.is_visible.data


def _process_uploaded_photos(form: VehicleForm, vehicle: Vehicle) -> list[str]:
    errors = []
    files = [f for f in (form.photos.data or []) if f and f.filename]
    if not files:
        return errors

    existing_count = len(vehicle.images)
    if existing_count + len(files) > current_app.config["MAX_IMAGES_PER_VEHICLE"]:
        errors.append(f"Máximo de {current_app.config['MAX_IMAGES_PER_VEHICLE']} fotos por viatura.")
        return errors

    next_order = (max((img.sort_order for img in vehicle.images), default=-1)) + 1
    has_primary = any(img.is_primary for img in vehicle.images)

    for file_storage in files:
        error = validate_image(file_storage)
        if error:
            errors.append(error)
            continue
        try:
            uploaded = upload_vehicle_image(file_storage, vehicle.slug)
        except Exception:
            errors.append(f"Falha ao enviar '{file_storage.filename}'. Tente novamente.")
            continue
        image = VehicleImage(
            vehicle=vehicle,
            image_url=uploaded["url"],
            public_id=uploaded["public_id"],
            is_primary=not has_primary,
            sort_order=next_order,
        )
        has_primary = True
        next_order += 1
        db.session.add(image)

    return errors


@admin_bp.route("/vehicles/add", methods=["GET", "POST"])
@login_required
def vehicle_add():
    form = VehicleForm()
    if form.validate_on_submit():
        vehicle = Vehicle(slug=unique_slug(f"{form.brand.data}-{form.model.data}-{form.year.data}"))
        _apply_form_to_vehicle(form, vehicle)
        db.session.add(vehicle)
        db.session.flush()

        upload_errors = _process_uploaded_photos(form, vehicle)
        db.session.commit()

        if upload_errors:
            for err in upload_errors:
                flash(err, "error")
        flash("Viatura adicionada com sucesso.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/vehicle_form.html", form=form, vehicle=None, mode="add")


@admin_bp.route("/vehicles/<int:vehicle_id>/edit", methods=["GET", "POST"])
@login_required
def vehicle_edit(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = VehicleForm(obj=vehicle)

    if form.validate_on_submit():
        if f"{form.brand.data}-{form.model.data}-{form.year.data}" != f"{vehicle.brand}-{vehicle.model}-{vehicle.year}":
            vehicle.slug = unique_slug(f"{form.brand.data}-{form.model.data}-{form.year.data}", exclude_id=vehicle.id)
        _apply_form_to_vehicle(form, vehicle)

        upload_errors = _process_uploaded_photos(form, vehicle)
        db.session.commit()

        if upload_errors:
            for err in upload_errors:
                flash(err, "error")
        flash("Alterações guardadas com sucesso.", "success")
        return redirect(url_for("admin.dashboard"))

    if request.method == "GET":
        form.status.data = vehicle.status
        form.is_featured.data = vehicle.is_featured
        form.is_visible.data = vehicle.is_visible

    delete_image_form = DeleteImageForm()
    return render_template(
        "admin/vehicle_form.html",
        form=form,
        vehicle=vehicle,
        mode="edit",
        delete_image_form=delete_image_form,
    )


@admin_bp.route("/vehicles/<int:vehicle_id>/delete", methods=["POST"])
@login_required
def vehicle_delete(vehicle_id):
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    for image in list(vehicle.images):
        delete_vehicle_image(image.public_id)
    db.session.delete(vehicle)
    db.session.commit()
    flash(f"'{vehicle.title}' foi eliminada.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/vehicles/<int:vehicle_id>/status", methods=["POST"])
@login_required
def vehicle_status(vehicle_id):
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    new_status = request.form.get("status")
    if new_status not in VEHICLE_STATUSES:
        abort(400)
    vehicle.status = new_status
    db.session.commit()
    flash(f"Estado de '{vehicle.title}' atualizado para {vehicle.status_label}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/vehicles/<int:vehicle_id>/toggle-visibility", methods=["POST"])
@login_required
def vehicle_toggle_visibility(vehicle_id):
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    vehicle.is_visible = not vehicle.is_visible
    db.session.commit()
    flash("Visibilidade atualizada.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/vehicles/<int:vehicle_id>/toggle-featured", methods=["POST"])
@login_required
def vehicle_toggle_featured(vehicle_id):
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    vehicle.is_featured = not vehicle.is_featured
    db.session.commit()
    flash("Destaque atualizado.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/vehicles/<int:vehicle_id>/images/<int:image_id>/delete", methods=["POST"])
@login_required
def image_delete(vehicle_id, image_id):
    form = DeleteImageForm()
    if not form.validate_on_submit():
        abort(400)

    image = VehicleImage.query.filter_by(id=image_id, vehicle_id=vehicle_id).first_or_404()
    was_primary = image.is_primary
    delete_vehicle_image(image.public_id)
    db.session.delete(image)
    db.session.flush()

    if was_primary:
        next_image = (
            VehicleImage.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleImage.sort_order).first()
        )
        if next_image:
            next_image.is_primary = True

    db.session.commit()
    flash("Foto eliminada.", "success")
    return redirect(url_for("admin.vehicle_edit", vehicle_id=vehicle_id))


@admin_bp.route("/vehicles/<int:vehicle_id>/images/<int:image_id>/primary", methods=["POST"])
@login_required
def image_make_primary(vehicle_id, image_id):
    form = DeleteImageForm()
    if not form.validate_on_submit():
        abort(400)

    VehicleImage.query.filter_by(vehicle_id=vehicle_id).update({"is_primary": False})
    image = VehicleImage.query.filter_by(id=image_id, vehicle_id=vehicle_id).first_or_404()
    image.is_primary = True
    db.session.commit()
    flash("Foto principal atualizada.", "success")
    return redirect(url_for("admin.vehicle_edit", vehicle_id=vehicle_id))
