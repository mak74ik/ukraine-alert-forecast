"""
Kinematic and spatial vector propagation engine for airborne threats across Ukraine.
Calculates Estimated Time of Arrival (ETA) windows and probability vectors.
"""
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional, Union, Any
from app.data.regions import REGIONS
from app.collector.threat_types import ThreatType, THREAT_DETAILS

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in km."""
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class ThreatProjection:
    def __init__(
        self,
        target_region_id: str,
        threat_type: ThreatType,
        source_region_id: str,
        eta_start: datetime,
        eta_end: datetime,
        probability: float,
        confidence: float,
        reason: str
    ):
        self.target_region_id = target_region_id
        self.threat_type = threat_type
        self.source_region_id = source_region_id
        self.eta_start = eta_start
        self.eta_end = eta_end
        self.probability = probability
        self.confidence = confidence
        self.reason = reason

    def to_dict(self) -> Dict:
        return {
            "target_region_id": self.target_region_id,
            "threat_type": self.threat_type.value if hasattr(self.threat_type, "value") else str(self.threat_type),
            "source_region_id": self.source_region_id,
            "eta_start": self.eta_start.isoformat(),
            "eta_end": self.eta_end.isoformat(),
            "time_window_str": f"{self.eta_start.strftime('%H:%M')} - {self.eta_end.strftime('%H:%M')}",
            "probability": round(self.probability, 3),
            "confidence": round(self.confidence, 3),
            "reason": self.reason
        }

def project_threat_trajectory(
    origin_or_event: Any,
    threat_type: Optional[ThreatType] = None,
    start_time: Optional[datetime] = None,
    direction: Optional[str] = None
) -> List[ThreatProjection]:
    """
    Simulates physical propagation of threat from origin oblast to neighboring & downstream oblasts.
    Accepts either (event) or (origin_region_id, threat_type, start_time, direction).
    """
    if hasattr(origin_or_event, "region_ids"):
        # ThreatEvent object passed
        event = origin_or_event
        if not event.region_ids:
            return []
        origin_region_id = event.region_ids[0]
        th_type = event.threat_type
        t_start = datetime.now(timezone.utc)
        dir_val = event.direction
    else:
        origin_region_id = origin_or_event
        th_type = threat_type or ThreatType.GENERAL_ALERT
        t_start = start_time or datetime.now(timezone.utc)
        dir_val = direction

    if origin_region_id not in REGIONS:
        return []

    origin = REGIONS[origin_region_id]
    th_key = ThreatType(th_type) if th_type in [t.value for t in ThreatType] else (th_type if isinstance(th_type, ThreatType) else ThreatType.GENERAL_ALERT)
    speed = THREAT_DETAILS.get(th_key, {}).get("avg_speed_kmh", 180.0)
    if speed <= 0:
        return []

    projections = []
    
    # 1. Immediate origin region threat
    dur_min = THREAT_DETAILS.get(th_key, {}).get("avg_duration_min", 45)
    projections.append(ThreatProjection(
        target_region_id=origin_region_id,
        threat_type=th_key,
        source_region_id=origin_region_id,
        eta_start=t_start,
        eta_end=t_start + timedelta(minutes=dur_min),
        probability=0.95,
        confidence=0.90,
        reason=f"Безпосередня фіксація загрози в області ({THREAT_DETAILS.get(th_key, {}).get('title', 'Загроза')})"
    ))

    # 2. Propagation to 1st and 2nd degree neighbors
    visited = {origin_region_id: 0.0}
    queue: List[Tuple[str, float, int]] = [(origin_region_id, 0.0, 0)]

    while queue:
        curr_id, dist_accum, hops = queue.pop(0)
        if hops >= 2:
            continue

        curr_reg = REGIONS.get(curr_id)
        if not curr_reg:
            continue

        for neighbor_id in curr_reg.get("neighbors", []):
            if neighbor_id in REGIONS and neighbor_id != origin_region_id:
                neighbor_reg = REGIONS[neighbor_id]
                segment_dist = haversine_distance_km(
                    curr_reg["lat"], curr_reg["lon"],
                    neighbor_reg["lat"], neighbor_reg["lon"]
                )
                total_dist = dist_accum + segment_dist

                if neighbor_id not in visited or total_dist < visited[neighbor_id]:
                    visited[neighbor_id] = total_dist
                    queue.append((neighbor_id, total_dist, hops + 1))

                    # Calculate ETA window
                    flight_time_hours = total_dist / speed
                    flight_time_mins = flight_time_hours * 60.0

                    tolerance_mins = 8.0 + (hops * 5.0)
                    eta_start = t_start + timedelta(minutes=max(0.0, flight_time_mins - tolerance_mins))
                    eta_end = t_start + timedelta(minutes=flight_time_mins + tolerance_mins + (dur_min * 0.5))

                    dir_boost = 1.0
                    if dir_val:
                        dlat = neighbor_reg["lat"] - origin["lat"]
                        dlon = neighbor_reg["lon"] - origin["lon"]
                        if dir_val == "west" and dlon < -0.5:
                            dir_boost = 1.35
                        elif dir_val == "north" and dlat > 0.5:
                            dir_boost = 1.35
                        elif dir_val == "south" and dlat < -0.5:
                            dir_boost = 1.35
                        elif dir_val == "east" and dlon > 0.5:
                            dir_boost = 1.35

                    decay = math.exp(-0.0035 * total_dist) * (0.85 ** hops) * dir_boost
                    prob = min(0.92, max(0.20, decay * 0.85))

                    projections.append(ThreatProjection(
                        target_region_id=neighbor_id,
                        threat_type=th_key,
                        source_region_id=origin_region_id,
                        eta_start=eta_start,
                        eta_end=eta_end,
                        probability=prob,
                        confidence=0.85 / (hops + 1),
                        reason=f"Курс загрози з {origin['name_ua']} (дистанція ~{int(total_dist)} км, підліт через ~{int(flight_time_mins)} хв)"
                    ))

    return projections
