"""
Main FastAPI Application Entry Point (100% Autonomous & Open Standalone Edition).
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

from app.config import settings
from app.database import init_db, get_active_alerts
from app.collector.open_monitor import OpenMonitoringService
from app.api.routes import router as api_router, set_monitor_service
from app.api.ws import ws_manager
from app.engine.forecaster import AlertForecaster

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app")

forecaster = AlertForecaster()
monitor_service: OpenMonitoringService = None

async def broadcast_threat_callback(event, projections=None):
    """Callback when monitor parses a new event -> pushes WebSocket update."""
    try:
        active = await get_active_alerts()
        overview = forecaster.get_national_overview(active, monitor_service.active_projections if monitor_service else [])
        await ws_manager.broadcast_json({
            "type": "THREAT_UPDATE",
            "event": event.to_dict(),
            "overview": overview
        })
    except Exception as e:
        logger.error(f"Broadcast error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global monitor_service
    logger.info("Initializing Database...")
    await init_db()

    logger.info("Starting Open Autonomous Monitoring & Forecasting Service (Zero API Keys needed)...")
    monitor_service = OpenMonitoringService(on_event_callback=broadcast_threat_callback)
    set_monitor_service(monitor_service)
    await monitor_service.start()

    yield

    logger.info("Shutting down services...")
    if monitor_service:
        await monitor_service.stop()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep alive / ping
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Mount Static UI Files
import sys

def _get_static_dir() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_path = Path(sys._MEIPASS) / "app" / "static"
        if bundle_path.exists():
            return bundle_path
    local_path = Path(__file__).resolve().parent / "static"
    local_path.mkdir(parents=True, exist_ok=True)
    return local_path

static_dir = _get_static_dir()
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
