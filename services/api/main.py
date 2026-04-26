"""Autonomous AI Negotiator (AAN) - FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.core.settings import get_settings
from config.database import init_db
from config.database.connection import get_db
from services.api.routes import jobs, listings
from services.api.routes.dashboard import router as dashboard_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(listings.router)
app.include_router(dashboard_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AAN API"}


@app.get("/")
async def root():
    return {"message": "Autonomous AI Negotiator API", "version": "1.0.0"}