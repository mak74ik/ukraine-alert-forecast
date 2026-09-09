from enum import Enum
from typing import Dict, Any

class AlertLevel(str, Enum):
    YELLOW = "YELLOW"    # Жовтий: загроза БПЛА (шахеди/дрони)
    ORANGE = "ORANGE"    # Помаранчевий: тактична авіація / КАБ
    RED = "RED"          # Червоний: ракетна небезпека / балістика / масований удар
    CLEAR = "CLEAR"      # Зелений: відбій загрози

ALERT_LEVEL_META: Dict[AlertLevel, Dict[str, Any]] = {
    AlertLevel.YELLOW: {
        "title": "Жовтий рівень (БПЛА)",
        "color": "#eab308",
        "fill_color": "#eab308",
        "border_color": "#facc15",
        "badge_class": "bg-yellow-500/20 text-yellow-300 border border-yellow-500/40",
        "description": "Загроза ударних дронів (Шахеди). Робота закладів дозволена за наявності укриття.",
        "icon": "fa-paper-plane",
        "rule": "Дозволено продовжувати роботу при доступі до укриття"
    },
    AlertLevel.RED: {
        "title": "Червоний рівень (Ракети / Балістика)",
        "color": "#ef4444",
        "fill_color": "#ef4444",
        "border_color": "#f87171",
        "badge_class": "bg-red-500/20 text-red-300 border border-red-500/40",
        "description": "Пряма ракетна або балістична загроза! Негайно пройдіть в укриття!",
        "icon": "fa-triangle-exclamation",
        "rule": "Зупинка роботи, негайний перехід в укриття"
    },
    AlertLevel.ORANGE: {
        "title": "Помаранчевий рівень (КАБ / Авіація)",
        "color": "#f97316",
        "fill_color": "#f97316",
        "border_color": "#fb923c",
        "badge_class": "bg-orange-500/20 text-orange-300 border border-orange-500/40",
        "description": "Загроза керованих авіабомб (КАБ) та активність тактичної авіації.",
        "icon": "fa-bullseye",
        "rule": "Підвищена небезпека у прифронтових районах"
    },
    AlertLevel.CLEAR: {
        "title": "Відбій загрози",
        "color": "#15803d",
        "fill_color": "#15803d",
        "border_color": "#22c55e",
        "badge_class": "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40",
        "description": "Повітряна тривога завершена. Небезпеки немає.",
        "icon": "fa-shield-check",
        "rule": "Штатний режим"
    }
}

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

THREAT_TO_ALERT_LEVEL: Dict[ThreatType, AlertLevel] = {
    ThreatType.SHAHED: AlertLevel.YELLOW,
    ThreatType.RECON_UAV: AlertLevel.YELLOW,
    ThreatType.MIG31K: AlertLevel.RED,
    ThreatType.STRATEGIC_AVIATION: AlertLevel.RED,
    ThreatType.STRATEGIC_TU: AlertLevel.RED,
    ThreatType.BALLISTIC: AlertLevel.RED,
    ThreatType.SEA_CRUISE: AlertLevel.RED,
    ThreatType.TACTICAL_AVIATION: AlertLevel.ORANGE,
    ThreatType.TACTICAL_KAB: AlertLevel.ORANGE,
    ThreatType.GENERAL_ALERT: AlertLevel.RED,
    ThreatType.ALL_CLEAR: AlertLevel.CLEAR,
}

THREAT_DETAILS: Dict[str, Dict[str, Any]] = {
    ThreatType.SHAHED: {
        "title": "Ударні БПЛА (Shahed/Герань)",
        "icon": "fa-paper-plane",
        "color": "#eab308",
        "alert_level": AlertLevel.YELLOW.value,
        "avg_speed_kmh": 165.0,
        "avg_duration_min": 120,
        "base_risk": 0.85
    },
    ThreatType.MIG31K: {
        "title": "Зліт МіГ-31К (Носій Кинджалів)",
        "icon": "fa-fighter-jet",
        "color": "#ef4444",
        "alert_level": AlertLevel.RED.value,
        "avg_speed_kmh": 3000.0,
        "avg_duration_min": 35,
        "base_risk": 0.95
    },
    ThreatType.STRATEGIC_AVIATION: {
        "title": "Стратегічна авіація (Ту-95МС / Ту-22М3)",
        "icon": "fa-plane-departure",
        "color": "#dc2626",
        "alert_level": AlertLevel.RED.value,
        "avg_speed_kmh": 850.0,
        "avg_duration_min": 180,
        "base_risk": 0.99
    },
    ThreatType.BALLISTIC: {
        "title": "Загроза балістики (Іскандер-М/С-300)",
        "icon": "fa-bomb",
        "color": "#b91c1c",
        "alert_level": AlertLevel.RED.value,
        "avg_speed_kmh": 6000.0,
        "avg_duration_min": 25,
        "base_risk": 0.90
    },
    ThreatType.TACTICAL_AVIATION: {
        "title": "Тактична авіація / КАБи",
        "icon": "fa-bullseye",
        "color": "#f97316",
        "alert_level": AlertLevel.ORANGE.value,
        "avg_speed_kmh": 900.0,
        "avg_duration_min": 45,
        "base_risk": 0.80
    },
    ThreatType.SEA_CRUISE: {
        "title": "Крилаті ракети (Калібр) з моря",
        "icon": "fa-water",
        "color": "#9333ea",
        "alert_level": AlertLevel.RED.value,
        "avg_speed_kmh": 880.0,
        "avg_duration_min": 60,
        "base_risk": 0.90
    },
    ThreatType.RECON_UAV: {
        "title": "Розвідувальний БПЛА",
        "icon": "fa-eye",
        "color": "#3b82f6",
        "alert_level": AlertLevel.YELLOW.value,
        "avg_speed_kmh": 120.0,
        "avg_duration_min": 60,
        "base_risk": 0.40
    },
    ThreatType.GENERAL_ALERT: {
        "title": "Повітряна тривога",
        "icon": "fa-triangle-exclamation",
        "color": "#ef4444",
        "alert_level": AlertLevel.RED.value,
        "avg_speed_kmh": 0.0,
        "avg_duration_min": 45,
        "base_risk": 0.70
    },
    ThreatType.ALL_CLEAR: {
        "title": "Відбій тривоги",
        "icon": "fa-shield-check",
        "color": "#22c55e",
        "alert_level": AlertLevel.CLEAR.value,
        "avg_speed_kmh": 0.0,
        "avg_duration_min": 0,
        "base_risk": 0.0
    }
}
