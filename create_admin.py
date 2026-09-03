"""
Creates or resets the single IN Motors owner/admin account.

Usage:
    python create_admin.py

Reads ADMIN_EMAIL and ADMIN_PASSWORD from the environment (.env). If either
is missing, you'll be prompted interactively (password input is hidden).
Safe to re-run: it updates the password hash if the account already exists.
"""
import getpass
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from extensions import db
from models import AdminUser


def main() -> None:
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD", "")

    if not email:
        email = input("Email do administrador: ").strip().lower()
    if not password:
        password = getpass.getpass("Palavra-passe do administrador: ")

    if not email or "@" not in email:
        print("Email inválido.", file=sys.stderr)
        sys.exit(1)
    if len(password) < 8:
        print("A palavra-passe deve ter pelo menos 8 caracteres.", file=sys.stderr)
        sys.exit(1)

    app = create_app()
    with app.app_context():
        user = AdminUser.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            print(f"Palavra-passe atualizada para {email}.")
        else:
            user = AdminUser(email=email)
            user.set_password(password)
            db.session.add(user)
            print(f"Conta de administrador criada para {email}.")
        db.session.commit()


if __name__ == "__main__":
    main()
