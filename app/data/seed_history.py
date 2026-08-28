"""
Precomputed empirical priors and historical pattern profiles for Ukrainian regions.
Provides realistic statistical baseline weights for 24h forecasting.
"""
import math
from typing import Dict, List
from app.data.regions import REGIONS
from app.collector.threat_types import ThreatType

def get_diurnal_threat_profile(threat_type: str, hour: int) -> float:
    """
    Returns baseline probability factor [0.0 - 1.0] for a threat type at a given UTC+2/3 hour (0..23).
    """
    if threat_type == ThreatType.SHAHED:
        # High at night (21:00 - 06:00), peak at 01:00-03:00, near zero during afternoon (11:00-17:00)
        if 21 <= hour or hour <= 6:
            # Gaussian bell curve around 2:00
            diff = (hour - 2) if hour <= 12 else (hour - 26)
            return float(0.85 * math.exp(-0.5 * (diff / 2.5) ** 2) + 0.15)
        elif 7 <= hour <= 9 or 19 <= hour <= 20:
            return 0.12
        else:
            return 0.03

    elif threat_type == ThreatType.MIG31K:
        # Bimodal daytime distribution: 10:00 - 13:00 and 15:00 - 18:00
        p1 = 0.55 * math.exp(-0.5 * ((hour - 11.5) / 1.8) ** 2)
        p2 = 0.50 * math.exp(-0.5 * ((hour - 16.5) / 1.8) ** 2)
        night = 0.10 if (23 <= hour or hour <= 5) else 0.05
        return float(max(p1, p2) + night)

    elif threat_type == ThreatType.STRATEGIC_AVIATION:
        # Peak at morning cruise missile strikes (04:00 - 07:00)
        diff = (hour - 5.5)
        return float(0.60 * math.exp(-0.5 * (diff / 1.6) ** 2) + 0.04)

    elif threat_type == ThreatType.BALLISTIC:
        # Uniform threat with slight evening & early morning elevation
        if (5 <= hour <= 8) or (20 <= hour <= 23):
            return 0.45
        return 0.30

    elif threat_type == ThreatType.TACTICAL_AVIATION:
        # Daytime frontline KAB strikes (09:00 - 20:00)
        if 8 <= hour <= 21:
            return float(0.70 * math.sin((hour - 8) / 13.0 * math.pi) + 0.20)
        return 0.15

    else:
        return 0.20

def calculate_regional_base_risk(region_id: str, hour: int) -> Dict[str, float]:
    """Calculate hourly base risk per threat type for a specific region."""
    region_info = REGIONS.get(region_id, {"risk_weight": 0.5})
    weight = region_info["risk_weight"]
    
    # Specific geographical adjustments
    is_frontline = region_id in ["UA-63", "UA-14", "UA-44", "UA-23", "UA-65", "UA-59", "UA-74", "UA-12"]
    is_western = region_id in ["UA-46", "UA-07", "UA-56", "UA-61", "UA-26", "UA-21", "UA-77", "UA-68"]
    is_capital = region_id in ["UA-30", "UA-32"]

    threats = [
        ThreatType.SHAHED,
        ThreatType.MIG31K,
        ThreatType.BALLISTIC,
        ThreatType.TACTICAL_AVIATION,
        ThreatType.STRATEGIC_AVIATION
    ]
    
    risk_breakdown = {}
    for threat in threats:
        diurnal = get_diurnal_threat_profile(threat, hour)
        
        # Spatial modifications
        multiplier = 1.0
        if threat == ThreatType.TACTICAL_AVIATION:
            multiplier = 1.6 if is_frontline else 0.15
        elif threat == ThreatType.BALLISTIC:
            multiplier = 1.4 if is_frontline else (1.1 if is_capital else 0.6)
        elif threat == ThreatType.SHAHED:
            multiplier = 1.2 if is_western or is_capital else 1.0
        elif threat == ThreatType.STRATEGIC_AVIATION:
            multiplier = 1.3 if is_capital or is_western else 0.9

        threat_p = min(0.98, max(0.01, diurnal * weight * multiplier))
        risk_breakdown[threat.value] = round(threat_p, 3)

    return risk_breakdown
