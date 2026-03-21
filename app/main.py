from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.event import router as event_router
from app.api.v1.enum import router as enum_router
from app.admin.admin import setup_admin
from app.admin.views import UserAdmin, EventAdmin, SessionAdmin, CategoryAdmin

app = FastAPI()

app.include_router(auth_router)
app.include_router(event_router)
app.include_router(enum_router)


# admin = setup_admin(app)
# admin.add_view(UserAdmin)
# admin.add_view(EventAdmin)
# admin.add_view(SessionAdmin)
# admin.add_view(CategoryAdmin)
