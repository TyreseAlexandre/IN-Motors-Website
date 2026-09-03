from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "admin.login"
login_manager.login_message = "Inicie sessão para aceder ao painel administrativo."
login_manager.login_message_category = "error"
