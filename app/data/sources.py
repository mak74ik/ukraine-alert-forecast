"""
Comprehensive multi-source registry of 25+ open channels, official feeds, and siren APIs.
"""
from typing import List, Tuple

# 25+ Open Monitoring Channels (Public Web Mirrors, Zero Telegram Auth required)
EXPANDED_PUBLIC_WEB_FEEDS: List[Tuple[str, str, str]] = [
    # (URL, Channel Name, Category)
    ("https://t.me/s/kpszsu", "ПС ЗСУ (Офіційно)", "official_af"),
    ("https://t.me/s/air_alert_ua", "Оповіщення України", "official_alerts"),
    ("https://t.me/s/DSNS_GOV_UA", "ДСНС України (Офіційно)", "official_gov"),
    ("https://t.me/s/GeneralStaffZSU", "Генштаб ЗСУ", "official_gov"),
    ("https://t.me/s/operativnoZSU", "Оперативний ЗСУ", "operational"),
    ("https://t.me/s/vanek_nikolaev", "Николаевский Ванёк", "monitoring_radar"),
    ("https://t.me/s/radarradar_ua", "Радар Інфо", "radar"),
    ("https://t.me/s/war_monitor", "Військовий Монітор", "military_monitoring"),
    ("https://t.me/s/eRadarrua", "єРадар ППО", "radar"),
    ("https://t.me/s/monitorwarr", "Monitor War UA", "military_monitoring"),
    ("https://t.me/s/radar_raketa", "Радар Ракета / БПЛА", "radar"),
    ("https://t.me/s/u_radar", "U-Radar Україна", "radar"),
    ("https://t.me/s/kievreal1", "Київ Оперативний", "regional_center"),
    ("https://t.me/s/kharkiv_alerts", "Харків Тривога", "regional_east"),
    ("https://t.me/s/dnipro_alerts", "Дніпро Оперативний", "regional_east"),
    ("https://t.me/s/odesa_alerts", "Одеса Офіційно", "regional_south"),
    ("https://t.me/s/zaporizhzhia_alerts", "Запоріжжя Інфо", "regional_south"),
    ("https://t.me/s/mykolaiv_alerts", "Миколаїв Моніторинг", "regional_south"),
    ("https://t.me/s/sumy_alerts", "Суми Оповіщення", "regional_north"),
    ("https://t.me/s/chernihiv_alerts", "Чернігів Інфо", "regional_north"),
    ("https://t.me/s/poltava_alerts", "Полтава Моніторинг", "regional_center"),
    ("https://t.me/s/vinnytsia_alerts", "Вінниця Сповіщення", "regional_west"),
    ("https://t.me/s/khmelnytskyi_alerts", "Хмельницький Радар", "regional_west"),
    ("https://t.me/s/lviv_alerts", "Львів Оповіщення", "regional_west"),
    ("https://t.me/s/volyn_alerts", "Волинь Інфо", "regional_west"),
    ("https://t.me/s/cherkasy_alerts", "Черкаси Оперативний", "regional_center")
]

# Direct Open Siren State Telemetry APIs
OPEN_ALERT_APIS: List[str] = [
    "https://ubilling.net.ua/aerialalerts/",
    "https://api.alerts.in.ua/v1/alerts/active.json"
]
