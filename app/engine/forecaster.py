"""
24-Hour Air Raid Alert Forecasting Engine.
Physics-based trajectory projection, diurnal threat profiling, Markov transitions,
and sub-regional precision. Strictly configured to Ukrainian Local Time (Kyiv UTC+3 / EEST).
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional

from app.data.regions import REGIONS
from app.collector.threat_types import ThreatType, THREAT_DETAILS, AlertLevel, ALERT_LEVEL_META, THREAT_TO_ALERT_LEVEL
from app.data.seed_history import calculate_regional_base_risk
from app.engine.trajectory import project_threat_trajectory, ThreatProjection

# Ukrainian Timezone (Kyiv UTC+3)
KYIV_TZ = timezone(timedelta(hours=3))

class AlertForecaster:
    """Combines diurnal priors, real-time kinetic vectors, sub-regional granularity, and Markov transitions."""

    def __init__(self):
        pass

    def generate_timeline(
        self,
        region_id: str,
        active_alerts: Dict[str, Dict[str, Any]],
        recent_projections: List[ThreatProjection],
        horizon_hours: int = 24,
        step_minutes: int = 5,
        history_hours: int = 4
    ) -> Dict[str, Any]:
        now = datetime.now(KYIV_TZ)
        start_time = now - timedelta(hours=history_hours)
        end_time = now + timedelta(hours=horizon_hours)

        total_steps = int((end_time - start_time).total_seconds() / (step_minutes * 60))
        timeline_points = []

        is_currently_active = region_id in active_alerts
        active_threat_info = active_alerts.get(region_id, {})
        current_threat_type = active_threat_info.get("threat_type", ThreatType.GENERAL_ALERT.value)
        is_partial = active_threat_info.get("is_partial", 0) == 1
        sub_regions = active_threat_info.get("sub_regions", [])

        reg_projections = [p for p in recent_projections if p.target_region_id == region_id]

        high_risk_windows: List[Dict[str, Any]] = []
        current_window: Optional[Dict[str, Any]] = None

        reg_meta = REGIONS.get(region_id, {})
        reg_weight = reg_meta.get("risk_weight", 0.5)

        # Baseline calm probability for this region (3% - 10%)
        calm_base = float(min(0.12, max(0.03, 0.06 * reg_weight)))

        for i in range(total_steps):
            step_time = start_time + timedelta(minutes=i * step_minutes)
            is_past = step_time < (now - timedelta(minutes=step_minutes // 2))
            is_live = abs((step_time - now).total_seconds()) <= (step_minutes * 60 / 2)
            hour = step_time.hour

            threat_contributions = {
                ThreatType.SHAHED.value: 0.02,
                ThreatType.BALLISTIC.value: 0.02,
                ThreatType.MIG31K.value: 0.02,
                ThreatType.TACTICAL_KAB.value: 0.02
            }

            if is_past:
                # Historical ground truth
                if is_currently_active and (now - step_time).total_seconds() < 3600:
                    prob = 0.70 if is_partial else 0.98
                    dominant_threat = current_threat_type
                else:
                    prob = calm_base
                    dominant_threat = ThreatType.GENERAL_ALERT.value
            elif is_live:
                if is_currently_active:
                    prob = 0.70 if is_partial else 0.98
                    dominant_threat = current_threat_type
                else:
                    prob = calm_base
                    dominant_threat = ThreatType.GENERAL_ALERT.value
            else:
                # Future mathematical forecast
                prob = calm_base
                dominant_threat = ThreatType.GENERAL_ALERT.value

                # 1. Kinematic projection from active flying targets
                for proj in reg_projections:
                    if proj.eta_start <= step_time <= proj.eta_end:
                        proj_boost = proj.probability
                        prob = max(prob, proj_boost)
                        threat_contributions[proj.threat_type.value] = max(
                            threat_contributions.get(proj.threat_type.value, 0.0),
                            proj_boost
                        )

                # 2. Nighttime Shahed wave (22:30 - 04:30)
                if (22 <= hour or hour <= 4) and reg_weight > 0.4:
                    shahed_prob = min(0.65, 0.50 * reg_weight)
                    prob = max(prob, shahed_prob)
                    threat_contributions[ThreatType.SHAHED.value] = max(
                        threat_contributions.get(ThreatType.SHAHED.value, 0.0),
                        shahed_prob
                    )

                # 3. Frontline tactical KABs during active daytime (08:00 - 20:00)
                if 8 <= hour <= 20 and region_id in ["UA-63", "UA-23", "UA-14", "UA-59", "UA-65"]:
                    kab_prob = 0.60
                    prob = max(prob, kab_prob)
                    threat_contributions[ThreatType.TACTICAL_KAB.value] = max(
                        threat_contributions.get(ThreatType.TACTICAL_KAB.value, 0.0),
                        kab_prob
                    )

                if any(v > calm_base for v in threat_contributions.values()):
                    dominant_threat = max(threat_contributions, key=threat_contributions.get)

            final_prob = float(min(0.98, max(0.02, prob)))

            # Track high-risk windows (>= 45% probability)
            if not is_past:
                if final_prob >= 0.45:
                    if current_window is None:
                        current_window = {
                            "start": step_time,
                            "end": step_time + timedelta(minutes=step_minutes),
                            "max_prob": final_prob,
                            "threat": dominant_threat
                        }
                    else:
                        current_window["end"] = step_time + timedelta(minutes=step_minutes)
                        current_window["max_prob"] = max(current_window["max_prob"], final_prob)
                else:
                    if current_window is not None:
                        if (current_window["end"] - current_window["start"]).total_seconds() >= 600:
                            high_risk_windows.append(current_window)
                        current_window = None

            timeline_points.append({
                "time": step_time.isoformat(),
                "time_display": step_time.strftime("%H:%M"),
                "is_past": is_past,
                "is_live": is_live,
                "probability": round(final_prob, 3),
                "threat_type": dominant_threat,
                "threat_title": THREAT_DETAILS.get(ThreatType(dominant_threat) if dominant_threat in [t.value for t in ThreatType] else ThreatType.GENERAL_ALERT, {}).get("title", "Загроза"),
                "color": THREAT_DETAILS.get(ThreatType(dominant_threat) if dominant_threat in [t.value for t in ThreatType] else ThreatType.GENERAL_ALERT, {}).get("color", "#ea580c")
            })

        if current_window is not None:
            if (current_window["end"] - current_window["start"]).total_seconds() >= 600:
                high_risk_windows.append(current_window)

        formatted_windows = []
        for w in high_risk_windows:
            s_str = w["start"].strftime("%H:%M")
            e_str = w["end"].strftime("%H:%M")
            th_obj = ThreatType(w["threat"]) if w["threat"] in [t.value for t in ThreatType] else ThreatType.GENERAL_ALERT
            th_title = THREAT_DETAILS.get(th_obj, {}).get("title", "Загроза")
            formatted_windows.append({
                "interval_str": f"{s_str} - {e_str}",
                "start": w["start"].isoformat(),
                "end": w["end"].isoformat(),
                "probability": round(w["max_prob"] * 100, 1),
                "threat_type": w["threat"],
                "threat_title": th_title,
                "danger_level": "CRITICAL" if w["max_prob"] > 0.80 else ("HIGH" if w["max_prob"] > 0.60 else "ELEVATED")
            })

        future_probs = [p["probability"] for p in timeline_points if not p["is_past"]]
        avg_24h_risk = (sum(future_probs) / len(future_probs)) if future_probs else 0.15
        max_24h_risk = max(future_probs) if future_probs else 0.25

        cur_level = active_alerts[region_id].get("alert_level") if is_currently_active else AlertLevel.CLEAR.value
        if not cur_level:
            cur_level = AlertLevel.RED.value
        level_meta = ALERT_LEVEL_META.get(AlertLevel(cur_level) if cur_level in [l.value for l in AlertLevel] else AlertLevel.CLEAR, {})

        return {
            "region_id": region_id,
            "region_name": REGIONS.get(region_id, {}).get("name_ua", region_id),
            "generated_at": now.isoformat(),
            "is_active_now": is_currently_active,
            "is_partial": is_partial,
            "sub_regions": sub_regions,
            "current_threat": current_threat_type if is_currently_active else None,
            "alert_level": cur_level,
            "alert_level_title": level_meta.get("title", "Спокійно"),
            "alert_level_color": level_meta.get("color", "#15803d"),
            "alert_level_rule": level_meta.get("rule", "Штатний режим"),
            "avg_24h_risk": round(avg_24h_risk, 3),
            "max_24h_risk": round(max_24h_risk, 3),
            "high_risk_windows": formatted_windows,
            "timeline": timeline_points
        }

    def generate_national_time_matrix(
        self,
        active_alerts: Dict[str, Dict[str, Any]],
        recent_projections: List[ThreatProjection],
        horizon_hours: int = 24,
        step_minutes: int = 15,
        history_hours: int = 4
    ) -> Dict[str, Any]:
        now = datetime.now(KYIV_TZ)
        start_time = now - timedelta(hours=history_hours)
        end_time = now + timedelta(hours=horizon_hours)

        total_steps = int((end_time - start_time).total_seconds() / (step_minutes * 60))
        time_steps = []

        for i in range(total_steps):
            step_time = start_time + timedelta(minutes=i * step_minutes)
            is_past = step_time < (now - timedelta(minutes=step_minutes // 2))
            is_live = abs((step_time - now).total_seconds()) <= (step_minutes * 60 / 2)
            hour = step_time.hour

            step_regions = {}
            step_levels = {}
            step_partials = {}
            for reg_id, meta in REGIONS.items():
                is_active = reg_id in active_alerts
                is_part = active_alerts.get(reg_id, {}).get("is_partial", 0) == 1 if is_active else False
                reg_weight = meta.get("risk_weight", 0.5)
                calm_base = float(min(0.12, max(0.03, 0.06 * reg_weight)))

                reg_proj = [p for p in recent_projections if p.target_region_id == reg_id and p.eta_start <= step_time <= p.eta_end]
                proj_prob = max([p.probability for p in reg_proj], default=0.0)

                if is_past:
                    prob = 0.98 if is_active and (now - step_time).total_seconds() < 3600 else calm_base
                elif is_live:
                    prob = (0.70 if is_part else 0.98) if is_active else max(calm_base, proj_prob)
                else:
                    prob = max(calm_base, proj_prob)
                    if (22 <= hour or hour <= 4) and reg_weight > 0.4:
                        prob = max(prob, 0.50 * reg_weight)
                    if 8 <= hour <= 20 and reg_id in ["UA-63", "UA-23", "UA-14", "UA-59", "UA-65"]:
                        prob = max(prob, 0.60)

                final_p = round(min(0.98, max(0.02, prob)), 3)
                step_regions[reg_id] = final_p
                if is_part and is_live:
                    step_partials[reg_id] = True

                # Determine Alert Level (Sept 1 standard)
                if is_active and (is_live or (is_past and (now - step_time).total_seconds() < 3600)):
                    lvl = active_alerts[reg_id].get("alert_level")
                    if not lvl:
                        lvl = "RED"
                    step_levels[reg_id] = lvl
                elif final_p >= 0.25:
                    if any(p.threat_type == ThreatType.SHAHED for p in reg_proj) or (22 <= hour or hour <= 4):
                        step_levels[reg_id] = AlertLevel.YELLOW.value
                    elif any(p.threat_type in (ThreatType.BALLISTIC, ThreatType.MIG31K) for p in reg_proj):
                        step_levels[reg_id] = AlertLevel.RED.value
                    elif any(p.threat_type in (ThreatType.TACTICAL_KAB, ThreatType.TACTICAL_AVIATION) for p in reg_proj) or (8 <= hour <= 20 and reg_id in ["UA-63", "UA-23", "UA-14", "UA-59", "UA-65"]):
                        step_levels[reg_id] = AlertLevel.ORANGE.value
                    else:
                        step_levels[reg_id] = AlertLevel.YELLOW.value if final_p < 0.60 else AlertLevel.RED.value
                else:
                    step_levels[reg_id] = AlertLevel.CLEAR.value

            time_steps.append({
                "time": step_time.isoformat(),
                "time_display": step_time.strftime("%H:%M"),
                "is_past": is_past,
                "is_live": is_live,
                "regions_risk": step_regions,
                "regions_alert_level": step_levels,
                "partials": step_partials
            })

        return {
            "generated_at": now.isoformat(),
            "step_minutes": step_minutes,
            "total_steps": len(time_steps),
            "steps": time_steps
        }

    def get_national_overview(
        self,
        active_alerts: Dict[str, Dict[str, Any]],
        recent_projections: List[ThreatProjection]
    ) -> Dict[str, Any]:
        now = datetime.now(KYIV_TZ)
        regions_summary = []
        all_hotspots = []

        for reg_id, meta in REGIONS.items():
            is_active = reg_id in active_alerts
            is_partial = False
            sub_regions = []
            if is_active:
                alert_obj = active_alerts[reg_id]
                is_partial = alert_obj.get("is_partial", 0) == 1
                sub_regions = alert_obj.get("sub_regions", [])
                for sr in sub_regions:
                    all_hotspots.append(sr)

            reg_weight = meta.get("risk_weight", 0.5)
            calm_base = float(min(0.12, max(0.03, 0.06 * reg_weight)))

            reg_proj = [p for p in recent_projections if p.target_region_id == reg_id]
            proj_prob = max([p.probability for p in reg_proj], default=0.0)

            cur_prob = (0.70 if is_partial else 0.98) if is_active else max(calm_base, proj_prob)
            cur_threat = active_alerts[reg_id]["threat_type"] if is_active else (
                reg_proj[0].threat_type.value if reg_proj else ThreatType.GENERAL_ALERT.value
            )

            # Alert Level from active DB or projection
            if is_active:
                cur_level = active_alerts[reg_id].get("alert_level")
                if not cur_level:
                    cur_level = AlertLevel.RED.value
            elif cur_prob >= 0.35:
                if reg_proj and reg_proj[0].threat_type == ThreatType.SHAHED:
                    cur_level = AlertLevel.YELLOW.value
                elif reg_proj and reg_proj[0].threat_type in (ThreatType.BALLISTIC, ThreatType.MIG31K):
                    cur_level = AlertLevel.RED.value
                else:
                    cur_level = AlertLevel.YELLOW.value
            else:
                cur_level = AlertLevel.CLEAR.value

            level_meta = ALERT_LEVEL_META.get(AlertLevel(cur_level) if cur_level in [l.value for l in AlertLevel] else AlertLevel.CLEAR, {})

            regions_summary.append({
                "id": reg_id,
                "name_ua": meta["name_ua"],
                "name_en": meta["name_en"],
                "short_ua": meta["short_ua"],
                "lat": meta["lat"],
                "lon": meta["lon"],
                "is_active": is_active,
                "is_partial": is_partial,
                "sub_regions": sub_regions,
                "current_probability": round(cur_prob, 3),
                "threat_type": cur_threat,
                "alert_level": cur_level,
                "alert_level_title": level_meta.get("title", "Спокійно"),
                "alert_level_color": level_meta.get("color", "#15803d"),
                "alert_level_rule": level_meta.get("rule", "Штатний режим"),
                "threat_title": THREAT_DETAILS.get(ThreatType(cur_threat) if cur_threat in [t.value for t in ThreatType] else ThreatType.GENERAL_ALERT, {}).get("title", "Загроза")
            })

        active_count = sum(1 for r in regions_summary if r["is_active"])
        
        # Calculate near-term predicted alerts for upcoming 60-120 minutes
        near_term = []
        for reg_id, meta in REGIONS.items():
            if reg_id in active_alerts:
                continue
            projs = [p for p in recent_projections if p.target_region_id == reg_id and p.eta_start > now]
            if projs:
                p = projs[0]
                eta_min = max(2, int((p.eta_start - now).total_seconds() / 60))
                near_term.append({
                    "region_id": reg_id,
                    "name_ua": meta["name_ua"],
                    "threat_type": p.threat_type.value,
                    "threat_title": THREAT_DETAILS.get(p.threat_type, {}).get("title", "Загроза"),
                    "alert_level": AlertLevel.YELLOW.value if p.threat_type == ThreatType.SHAHED else AlertLevel.RED.value,
                    "eta_minutes": eta_min,
                    "probability": round(p.probability, 2),
                    "confidence": p.confidence
                })
        near_term.sort(key=lambda x: x["eta_minutes"])

        return {
            "timestamp": now.isoformat(),
            "active_alerts_count": active_count,
            "total_regions": len(regions_summary),
            "regions": regions_summary,
            "hotspots": all_hotspots,
            "near_term_predictions": near_term[:6]
        }
