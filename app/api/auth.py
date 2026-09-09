"""
Lightweight Native Telegram Profile & Channel Verification API.
Zero external API keys required; 100% non-blocking; completely optional for guests.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.data.sources import get_channels_by_region, REGIONAL_TELEGRAM_CHANNELS
from app.data.regions import REGIONS
from app.database import save_user_profile, get_user_profile

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    region_id: Optional[str] = "UA-32"

class SubscriptionConfirmRequest(BaseModel):
    username: str
    region_id: Optional[str] = "UA-32"
    channels: Optional[List[str]] = None

@router.post("/login")
async def native_login(req: LoginRequest):
    clean_name = req.username.strip().lstrip("@")
    if not clean_name:
        clean_name = "guest_monitor"
    
    reg_id = req.region_id if req.region_id in REGIONS else "UA-32"
    
    existing = await get_user_profile(clean_name)
    is_sub = existing.get("is_subscribed", False) if existing else False
    sub_channels = existing.get("subscribed_channels", []) if existing else []
    
    profile = await save_user_profile(
        username=clean_name,
        region_id=reg_id,
        is_subscribed=is_sub,
        channels=sub_channels
    )
    
    regional_channels = get_channels_by_region(reg_id)
    return {
        "status": "success",
        "profile": profile,
        "channels": regional_channels,
        "precision_mode": "ultra" if is_sub else "standard"
    }

@router.get("/me")
async def get_current_profile(username: Optional[str] = Query(None)):
    if not username:
        return {
            "authenticated": False,
            "profile": {
                "username": "guest",
                "region_id": "UA-32",
                "is_subscribed": False,
                "precision_mode": "standard"
            }
        }
    
    profile = await get_user_profile(username)
    if not profile:
        return {
            "authenticated": False,
            "profile": {
                "username": username.lstrip("@"),
                "region_id": "UA-32",
                "is_subscribed": False,
                "precision_mode": "standard"
            }
        }
    
    reg_id = profile.get("region_id", "UA-32")
    channels = get_channels_by_region(reg_id)
    return {
        "authenticated": True,
        "profile": profile,
        "channels": channels,
        "precision_mode": "ultra" if profile.get("is_subscribed") else "standard"
    }

@router.post("/confirm_subscription")
async def confirm_subscription(req: SubscriptionConfirmRequest):
    clean_name = req.username.strip().lstrip("@")
    reg_id = req.region_id if req.region_id in REGIONS else "UA-32"
    channels = req.channels or [c["username"] for c in get_channels_by_region(reg_id)]
    
    profile = await save_user_profile(
        username=clean_name,
        region_id=reg_id,
        is_subscribed=True,
        channels=channels
    )
    
    return {
        "status": "success",
        "message": "Підписку на канали успішно підтверджено! Надвисоку точність активовано.",
        "profile": profile,
        "precision_mode": "ultra"
    }

class ScanRegionRequest(BaseModel):
    region_id: str
    username: Optional[str] = None

class ScanChannelRequest(BaseModel):
    channel: str
    username: Optional[str] = None

@router.get("/channels/{region_id}")
async def get_region_channels_list(region_id: str):
    if region_id not in REGIONS:
        raise HTTPException(status_code=404, detail="Region not found")
    return {
        "region_id": region_id,
        "region_name": REGIONS[region_id]["name_ua"],
        "channels": get_channels_by_region(region_id)
    }

@router.post("/scan_region")
async def scan_region_now(req: ScanRegionRequest):
    from app.api.routes import monitor_service
    if not monitor_service:
        raise HTTPException(status_code=500, detail="Моніторинговий сервіс ще не запущено")
    
    reg_id = req.region_id if req.region_id in REGIONS else "UA-32"
    result = await monitor_service.scan_region_channels(reg_id)
    
    if req.username:
        clean = req.username.strip().lstrip("@")
        if clean:
            await save_user_profile(
                username=clean,
                region_id=reg_id,
                is_subscribed=True
            )

    return result

@router.post("/scan_channel")
async def scan_custom_channel(req: ScanChannelRequest):
    from app.api.routes import monitor_service
    if not monitor_service:
        raise HTTPException(status_code=500, detail="Моніторинговий сервіс ще не запущено")

    ch = req.channel.strip()
    if not ch:
        raise HTTPException(status_code=400, detail="Вкажіть посилання або username каналу")

    result = await monitor_service.scan_specific_channel(ch)
    
    if req.username and result.get("status") == "success":
        clean = req.username.strip().lstrip("@")
        profile = await get_user_profile(clean)
        if profile:
            current_channels = profile.get("subscribed_channels") or []
            if ch not in current_channels:
                current_channels.append(ch)
                await save_user_profile(
                    username=clean,
                    region_id=profile.get("region_id", "UA-32"),
                    is_subscribed=True,
                    channels=current_channels
                )

    return result
