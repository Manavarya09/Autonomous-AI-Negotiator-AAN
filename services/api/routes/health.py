"""System health and monitoring endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from config.database.connection import async_session_maker
from services.worker.scrapers.circuit_breaker import get_all_circuit_states

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("")
async def system_health():
    """Full system health check."""
    health = {
        "status": "healthy",
        "services": {},
    }
    
    try:
        async with async_session_maker() as db:
            await db.execute("SELECT 1")
            health["services"]["database"] = "healthy"
    except Exception:
        health["services"]["database"] = "unhealthy"
        health["status"] = "degraded"
    
    circuits = get_all_circuit_states()
    health["services"]["circuits"] = circuits
    
    from services.worker.scrapers.circuit_breaker import SCRAPER_CIRCUITS
    failed_circuits = [c for c in circuits if c["state"] == "open"]
    
    if failed_circuits:
        health["status"] = "degraded"
        health["services"]["scrapers"] = f"{len(failed_circuits)} platforms failing"
    else:
        health["services"]["scrapers"] = "healthy"
    
    return JSONResponse(
        content=health,
        status_code=200 if health["status"] == "healthy" else 503,
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    try:
        async with async_session_maker() as db:
            await db.execute("SELECT 1")
        return {"ready": True}
    except Exception:
        return JSONResponse({"ready": False}, status_code=503)


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"alive": True}