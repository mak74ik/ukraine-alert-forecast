from enum import Enum
from typing import Dict, Any

class ThreatType(str, Enum):
    SHAHED = "SHAHED"                    # UAV attack (Shahed-136/131)
    MIG31K = "MIG31K"                    # Kinzhal carrier MiG-31K
    STRATEGIC_AVIATION = "STRATEGIC_TU"  # Tu-95MS, Tu-22M3, Tu-160
    STRATEGIC_TU = "STRATEGIC_TU"
    BALLISTIC = "BALLISTIC"              # Iskander-M, KN-23, S-300/400
    TACTICAL_AVIATION = "TACTICAL_KAB"   # Tactical aviation (KAB / Kh-59)
    TACTICAL_KAB = "TACTICAL_KAB"
    SEA_CRUISE = "SEA_CRUISE"            # Kalibr cruise missiles
    RECON_UAV = "RECON_UAV"              # Reconnaissance drone
    GENERAL_ALERT = "GENERAL_ALERT"      # Alert started (unknown specific type)
    ALL_CLEAR = "ALL_CLEAR"              # Відбій тривоги

THREAT_DETAILS: Dict[str, Dict[str, Any]] = {
    ThreatType.SHAHED: {
        "title": "Ударні БПЛА (Shahed/Герань)",
        "icon": "fa-paper-plane",
        "color": "#eab308", # Yellow/Amber
        "avg_speed_kmh": 165.0,
        "avg_duration_min": 120,
        "base_risk": 0.85
    },
    ThreatType.MIG31K: {
        "title": "Зліт МіГ-31К (Носій Кинджалів)",
        "icon": "fa-fighter-jet",
        "color": "#ef4444", # Red
        "avg_speed_kmh": 3000.0,
        "avg_duration_min": 35,
        "base_risk": 0.95
    },
    ThreatType.STRATEGIC_AVIATION: {
        "title": "Стратегічна авіація (Ту-95МС / Ту-22М3)",
        "icon": "fa-plane-departure",
        "color": "#dc2626", # Dark Red
        "avg_speed_kmh": 850.0,
        "avg_duration_min": 180,
        "base_risk": 0.99
    },
    ThreatType.BALLISTIC: {
        "title": "Загроза балістики (Іскандер-М/С-300)",
        "icon": "fa-bomb",
        "color": "#b91c1c", # Deep Red
        "avg_speed_kmh": 6000.0,
        "avg_duration_min": 25,
        "base_risk": 0.90
    },
    ThreatType.TACTICAL_AVIATION: {
        "title": "Тактична авіація / КАБи",
        "icon": "fa-bullseye",
        "color": "#f97316", # Orange
        "avg_speed_kmh": 900.0,
        "avg_duration_min": 45,
        "base_risk": 0.80
    },
    ThreatType.SEA_CRUISE: {
        "title": "Крилаті ракети (Калібр) з моря",
        "icon": "fa-water",
        "color": "#9333ea", # Purple
        "avg_speed_kmh": 880.0,
        "avg_duration_min": 60,
        "base_risk": 0.90
    },
    ThreatType.RECON_UAV: {
        "title": "Розвідувальний БПЛА",
        "icon": "fa-eye",
        "color": "#3b82f6", # Blue
        "avg_speed_kmh": 120.0,
        "avg_duration_min": 60,
        "base_risk": 0.40
    },
    ThreatType.GENERAL_ALERT: {
        "title": "Повітряна тривога",
        "icon": "fa-triangle-exclamation",
        "color": "#ea580c",
        "avg_speed_kmh": 0.0,
        "avg_duration_min": 45,
        "base_risk": 0.70
    },
    ThreatType.ALL_CLEAR: {
        "title": "Відбій тривоги",
        "icon": "fa-shield-check",
        "color": "#22c55e", # Green
        "avg_speed_kmh": 0.0,
        "avg_duration_min": 0,
        "base_risk": 0.0
    }
}
