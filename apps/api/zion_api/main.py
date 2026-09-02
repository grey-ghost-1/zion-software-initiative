"""FastAPI application entry point."""

from fastapi import FastAPI

from zion_api.routes.health import router as health_router

app = FastAPI(
    title="Zion API",
    description="Foundation-stage API for the Zion Software Initiative.",
    version="0.1.0",
)
app.include_router(health_router)
