from sqladmin import Admin
from app.db.database import engine


def setup_admin(app):
    admin = Admin(app, engine)
    return admin