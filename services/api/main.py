"""Autonomous AI Negotiator (AAN) - FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import json
import asyncio

from config.core.settings import get_settings
from config.database import init_db
from services.api.routes import jobs, listings
from services.api.routes.dashboard import router as dashboard_router


settings = get_settings()

active_connections: Dict[str, List[WebSocket]] = {}


async def notify_job_update(job_id: str, event: dict):
    """Send update to all connected clients for a job."""
    if job_id in active_connections:
        for connection in active_connections[job_id]:
            try:
                await connection.send_json(event)
            except:
                pass


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


@app.websocket("/ws/jobs/{job_id}")
async def websocket_job_updates(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job updates."""
    await websocket.accept()
    
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)
    
    try:
        await websocket.send_json({
            "event": "connected",
            "job_id": job_id,
            "message": "Connected to job updates"
        })
        
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            
            if data_json.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if job_id in active_connections:
            active_connections[job_id].remove(websocket)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AAN API"}


@app.get("/")
async def root():
    return {"message": "Autonomous AI Negotiator API", "version": "1.0.0"}