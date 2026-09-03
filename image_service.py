import cloudinary
import cloudinary.uploader
from flask import current_app

CLOUDINARY_FOLDER = "in-motors/vehicles"


def configure_cloudinary(app) -> None:
    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )


def _allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def validate_image(file_storage) -> str | None:
    """Returns an error message if the file is invalid, otherwise None."""
    if not file_storage or not file_storage.filename:
        return None
    if not _allowed_file(file_storage.filename):
        return f"'{file_storage.filename}' não é um tipo de imagem permitido (use JPG, PNG ou WEBP)."

    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > current_app.config["MAX_IMAGE_SIZE"]:
        max_mb = current_app.config["MAX_IMAGE_SIZE"] // (1024 * 1024)
        return f"'{file_storage.filename}' excede o tamanho máximo de {max_mb}MB."
    if size == 0:
        return None
    return None


def upload_vehicle_image(file_storage, vehicle_slug: str) -> dict:
    result = cloudinary.uploader.upload(
        file_storage,
        folder=f"{CLOUDINARY_FOLDER}/{vehicle_slug}",
        resource_type="image",
        allowed_formats=list(current_app.config["ALLOWED_IMAGE_EXTENSIONS"]),
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}


def delete_vehicle_image(public_id: str) -> None:
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        current_app.logger.exception("Failed to delete Cloudinary asset %s", public_id)
