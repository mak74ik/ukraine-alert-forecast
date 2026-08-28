import os
from pathlib import Path
from typing import List

class Settings:
    APP_NAME: str = "UA Air Raid Alert Forecast & Monitor"
    APP_VERSION: str = "2.0.0 (Open Standalone Edition)"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///alerts_data.db"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Public Open Data & Web Feeds (Zero authentication required)
    OPEN_FEED_POLL_INTERVAL_SEC: int = int(os.getenv("OPEN_FEED_POLL_INTERVAL_SEC", "30"))
    
    # Public web channels / RSS mirrors that require NO telegram account/API keys
    PUBLIC_WEB_FEEDS: List[str] = [
        "https://t.me/s/kpszsu",          # Public web preview of Air Force (no login needed)
        "https://t.me/s/air_alert_ua",    # Public web preview of alerts
        "https://t.me/s/vanek_nikolaev",  # Public web preview of monitoring
        "https://t.me/s/radarradar_ua"    # Public web preview of radar
    ]

    # Prediction Model Settings
    FORECAST_HORIZON_HOURS: int = 24
    TIMELINE_STEP_MINUTES: int = 5
    DRONE_SPEED_KMH: float = 165.0  # Shahed-136 avg speed
    CRUISE_MISSILE_SPEED_KMH: float = 850.0  # Kh-101/Kalibr avg speed
    BALLISTIC_FLIGHT_TIME_MIN: float = 4.0   # Iskander-M / S-300 flight time

settings = Settings()
