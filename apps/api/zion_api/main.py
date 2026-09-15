"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from zion_api.core.config import get_settings
from zion_api.core.errors import register_exception_handlers
from zion_api.core.logging import configure_logging
from zion_api.core.middleware import RequestIDMiddleware
from zion_api.routes.admin import router as admin_router
from zion_api.routes.auth import router as auth_router
from zion_api.routes.health import router as health_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Zion API",
    description="Foundation-stage modular API for the Zion Software Initiative.",
    version="0.2.0",
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
