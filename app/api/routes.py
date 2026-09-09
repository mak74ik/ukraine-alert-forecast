from app.api.auth import router as auth_router
from app.data.sources import get_channels_by_region
"""
FastAPI REST routes for alerts, 24h forecasts, live logs, matrix scrubber, radar tracks, and simulation triggers.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.data.regions import REGIONS
from app.database import get_active_alerts, get_recent_threat_logs, get_recent_alerts_history
from app.engine.forecaster import AlertForecaster
from app.engine.radar_targets import radar_service
from app.collector.threat_types import ThreatType, THREAT_DETAILS
from app.api.ws import ws_manager

router = APIRouter(prefix="/api")
router.include_router(auth_router)
forecaster = AlertForecaster()

monitor_service = None

def set_monitor_service(service):
    global monitor_service
    monitor_service = service

class SimulateRequest(BaseModel):
    text: str
    channel: Optional[str] = "@manual_input"

@router.get("/regions")
async def get_regions_list():
    return [
        {
            "id": r["id"],
            "name_ua": r["name_ua"],
            "name_en": r["name_en"],
            "name_ru": r["name_ru"],
            "short_ua": r["short_ua"],
            "lat": r["lat"],
            "lon": r["lon"],
            "neighbors": r["neighbors"],
            "risk_weight": r["risk_weight"]
        }
        for r in REGIONS.values()
    ]

@router.get("/overview")
async def get_overview():
    active = await get_active_alerts()
    projections = monitor_service.active_projections if monitor_service else []
    overview = forecaster.get_national_overview(active, projections)
    overview["radar_tracks"] = radar_service.get_live_radar_tracks()
    return overview

@router.get("/radar")
async def get_radar_tracks():
    """Returns live airborne targets like neptun.in.ua (Shaheds, missiles, jets)."""
    return radar_service.get_live_radar_tracks()

@router.get("/matrix")
async def get_national_matrix():
    active = await get_active_alerts()
    projections = monitor_service.active_projections if monitor_service else []
    return forecaster.generate_national_time_matrix(
        active_alerts=active,
        recent_projections=projections,
        horizon_hours=24,
        step_minutes=15,
        history_hours=4
    )

@router.get("/forecast/{region_id}")
async def get_region_forecast(region_id: str):
    if region_id not in REGIONS:
        raise HTTPException(status_code=404, detail="Region not found")

    active = await get_active_alerts()
    projections = monitor_service.active_projections if monitor_service else []
    
    forecast_data = forecaster.generate_timeline(
        region_id=region_id,
        active_alerts=active,
        recent_projections=projections,
        horizon_hours=24,
        step_minutes=5,
        history_hours=4
    )
    return forecast_data

@router.get("/logs")
async def get_threat_logs(limit: int = 40):
    return await get_recent_threat_logs(limit=limit)

@router.post("/sync_now")
async def sync_alerts_now():
    if not monitor_service:
        raise HTTPException(status_code=500, detail="Monitor service not ready")
    success = await monitor_service.sync_real_active_alerts()
    active = await get_active_alerts()
    overview = forecaster.get_national_overview(active, monitor_service.active_projections)
    overview["radar_tracks"] = radar_service.get_live_radar_tracks()
    await ws_manager.broadcast_json({
        "type": "THREAT_UPDATE",
        "overview": overview
    })
    return {"status": "success" if success else "failed", "active_count": len(active)}

@router.post("/simulate")
async def simulate_event(req: SimulateRequest):
    if not monitor_service:
        raise HTTPException(status_code=500, detail="Monitor service not ready")

    event = await monitor_service.process_raw_message(req.text, channel=req.channel)
    if not event:
        return {"status": "ignored", "reason": "No actionable threat or region identified in text"}

    active = await get_active_alerts()
    radar_service.create_or_update_target_from_event(event, active)
    overview = forecaster.get_national_overview(active, monitor_service.active_projections)
    overview["radar_tracks"] = radar_service.get_live_radar_tracks()

    await ws_manager.broadcast_json({
        "type": "NEW_THREAT_EVENT",
        "event": event.to_dict(),
        "overview": overview
    })

    return {
        "status": "success",
        "event": event.to_dict(),
        "active_regions_count": len(event.region_ids),
        "radar_targets": radar_service.get_live_radar_tracks()
    }

@router.get("/channels/{region_id}")
async def get_region_channels(region_id: str):
    if region_id not in REGIONS:
        raise HTTPException(status_code=404, detail="Region not found")
    return {
        "region_id": region_id,
        "name_ua": REGIONS[region_id]["name_ua"],
        "channels": get_channels_by_region(region_id)
    }
