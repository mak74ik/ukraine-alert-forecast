"""
High-performance local text & threat extractor (Zero external LLMs/APIs).
Analyzes monitoring posts in Ukrainian and Russian using rule engines,
stem/regex patterns, directional graph heuristics, and sub-regional city/raion extraction.
"""
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from app.collector.threat_types import ThreatType
from app.data.regions import find_regions_by_text, REGIONS
from app.data.cities import find_sub_regions_by_text

THREAT_PATTERNS = [
    # MiG-31K
    (
        r"(зліт|взлет|активність|активность).*(міг-31к|миг-31к|mig-31|кінжал|кинджал|кинжал)",
        ThreatType.MIG31K
    ),
    (
        r"(міг-31к|миг-31к|mig-31k)",
        ThreatType.MIG31K
    ),
    # Strategic Aviation (Tu-95 / Tu-22)
    (
        r"(ту-95|ту-22|ту-160|tu-95|tu-22|стратегічн|стратегическ|страти|пуски.*х-101|х-555|х-22|пуски.*крилатих)",
        ThreatType.STRATEGIC_AVIATION
    ),
    # Ballistics / S-300 / Iskander
    (
        r"(балістик|баллистик|іскандер-м|искандер-м|с-300|с-400|kn-23|кн-23|загроза застосування баліст|загроза баліст)",
        ThreatType.BALLISTIC
    ),
    # Shahed / UAV
    (
        r"(шахед|шахід|шахеды|шахедов|бпла|дрони|дроны|мопед|герань|бплa|безпілотник|geran|shahed)",
        ThreatType.SHAHED
    ),
    # Sea cruise / Kalibr
    (
        r"(калібр|калибр|ракетоносій|ракетоноситель|з акваторії чорного|с акватории черного|чорне море|черное море)",
        ThreatType.SEA_CRUISE
    ),
    # Tactical Aviation / KAB
    (
        r"(каб|каби|кабы|керовані авіаційні|управляемые авиа|су-34|су-35|тактичн.*авіац|тактическ.*авиац|х-59|х-69)",
        ThreatType.TACTICAL_AVIATION
    ),
    # Recon UAV
    (
        r"(розвідник|разведчик|supercam|суперкам|zala|зала|орлан-10|orlan)",
        ThreatType.RECON_UAV
    )
]

ALL_CLEAR_PATTERNS = [
    r"(відбій|отбой|чисто|загроза минула|загрозу ліквідовано|відбій тривоги|отбой тревоги|локаційно втрачено|знищено)"
]

ALERT_START_PATTERNS = [
    r"(тривога|тревога|повітряна тривога|в укриття|пройдіть в укриття|загроза|увага|внимание|небезпека)"
]

DIRECTION_PATTERNS = {
    "north": [r"північ", r"север", r"чернігівщин", r"сумщин", r"на київ"],
    "south": [r"південь", r"юг", r"одещин", r"миколаївщин", r"херсон"],
    "west": [r"захід", r"запад", r"вінниччин", r"хмельниччин", r"львів", r"житомир"],
    "east": [r"схід", r"восток", r"харків", r"донбас", r"дніпро", r"запоріжжя"],
    "central": [r"центр", r"полтав", r"черкас", r"кіровоград"]
}


class ThreatEvent:
    def __init__(
        self,
        threat_type: ThreatType,
        is_clear: bool,
        region_ids: List[str],
        sub_regions: List[Dict[str, Any]],
        raw_text: str,
        channel: str,
        timestamp: datetime,
        source_id: Optional[str] = None,
        confidence: float = 0.85,
        estimated_duration_min: int = 45,
        direction: Optional[str] = None,
        is_partial: bool = False
    ):
        self.threat_type = threat_type
        self.is_clear = is_clear
        self.region_ids = region_ids
        self.sub_regions = sub_regions
        self.raw_text = raw_text
        self.channel = channel
        self.timestamp = timestamp
        self.source_id = source_id
        self.confidence = confidence
        self.estimated_duration_min = estimated_duration_min
        self.direction = direction
        self.is_partial = is_partial

    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_type": self.threat_type.value,
            "is_clear": self.is_clear,
            "region_ids": self.region_ids,
            "sub_regions": self.sub_regions,
            "is_partial": self.is_partial,
            "raw_text": self.raw_text,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "estimated_duration_min": self.estimated_duration_min,
            "direction": self.direction
        }


class LocalThreatParser:
    """Zero-LLM Fast NLP analyzer with sub-regional pinpoint detection."""

    def __init__(self):
        self.threat_patterns = [(re.compile(p, re.IGNORECASE), t) for p, t in THREAT_PATTERNS]
        self.clear_patterns = [re.compile(p, re.IGNORECASE) for p in ALL_CLEAR_PATTERNS]
        self.start_patterns = [re.compile(p, re.IGNORECASE) for p in ALERT_START_PATTERNS]

    def parse_message(self, text: str, channel: str = "monitoring", msg_time: Optional[datetime] = None) -> Optional[ThreatEvent]:
        if not text or len(text.strip()) < 3:
            return None

        clean_text = text.strip()
        timestamp = msg_time or datetime.now(timezone.utc)

        # 1. Check if ALL CLEAR
        is_clear = any(cp.search(clean_text) for cp in self.clear_patterns)
        
        # 2. Match threat type
        matched_threat = None
        for pattern, threat_type in self.threat_patterns:
            if pattern.search(clean_text):
                matched_threat = threat_type
                break
                
        if not matched_threat:
            if is_clear:
                matched_threat = ThreatType.ALL_CLEAR
            elif any(sp.search(clean_text) for sp in self.start_patterns):
                matched_threat = ThreatType.GENERAL_ALERT
            else:
                return None

        # 3. Find sub-regional cities / raions first
        sub_regions = find_sub_regions_by_text(clean_text)
        
        # 4. Find affected regions (oblasts)
        region_ids = find_regions_by_text(clean_text)
        for sr in sub_regions:
            if sr["region_id"] not in region_ids:
                region_ids.append(sr["region_id"])

        if matched_threat in (ThreatType.MIG31K, ThreatType.STRATEGIC_AVIATION) and not region_ids:
            region_ids = list(REGIONS.keys())

        # Determine if partial / localized to specific district/city
        is_partial = len(sub_regions) > 0 and len(region_ids) <= 2 and matched_threat not in (ThreatType.MIG31K, ThreatType.STRATEGIC_AVIATION)

        # 5. Extract direction
        direction = None
        for d_name, d_patterns in DIRECTION_PATTERNS.items():
            if any(re.search(dp, clean_text, re.IGNORECASE) for dp in d_patterns):
                direction = d_name
                break

        duration_map = {
            ThreatType.MIG31K: 35,
            ThreatType.STRATEGIC_AVIATION: 180,
            ThreatType.BALLISTIC: 25,
            ThreatType.SHAHED: 120,
            ThreatType.TACTICAL_AVIATION: 45,
            ThreatType.SEA_CRUISE: 60,
            ThreatType.RECON_UAV: 45,
            ThreatType.GENERAL_ALERT: 45,
            ThreatType.ALL_CLEAR: 0
        }
        est_duration = duration_map.get(matched_threat, 45)
        confidence = 0.95 if sub_regions else (0.90 if len(region_ids) > 0 else 0.75)

        return ThreatEvent(
            threat_type=matched_threat,
            is_clear=is_clear,
            region_ids=region_ids,
            sub_regions=sub_regions,
            raw_text=clean_text,
            channel=channel,
            timestamp=timestamp,
            confidence=confidence,
            estimated_duration_min=est_duration,
            direction=direction,
            is_partial=is_partial
        )
