from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.admin.admin import setup_admin
from app.admin.views import UserAdmin
app = FastAPI()

app.include_router(auth_router)

admin = setup_admin(app)
admin.add_view(UserAdmin)
