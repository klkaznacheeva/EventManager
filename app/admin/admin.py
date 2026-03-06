import os

from sqladmin import Admin
from sqladmin.templating import Jinja2Templates

from app.db.database import engine


def setup_admin(app):
    # текущая папка admin
    base_dir = os.path.dirname(__file__)
    templates_path = os.path.join(base_dir, "templates")  # <- убрали лишний "admin"

    admin = Admin(app, engine, templates_dir=templates_path)
    return admin