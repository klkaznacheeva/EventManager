from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.event import router as event_router
from app.api.v1.enum import router as enum_router
from app.admin.router import router as admin_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(event_router)
app.include_router(enum_router)
app.include_router(admin_router)
