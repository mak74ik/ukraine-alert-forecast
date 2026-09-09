from app.collector.threat_types import ThreatType, AlertLevel, THREAT_TO_ALERT_LEVEL
"""
Resilient SQLite database for storing alerts, threat logs, and empirical distributions.
Supports sub-regional granularity, localized districts, and fail-safe recovery.
"""
import sqlite3
import asyncio
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

def _get_app_db_path() -> Path:
    env_db = os.environ.get("ALERTS_DB_PATH")
    if env_db:
        p = Path(env_db)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    cwd_db = Path("alerts_data.db")
    if cwd_db.exists() and os.access(cwd_db, os.W_OK):
        return cwd_db

    # User Application Data directory
    app_dir = Path.home() / ".ua_alert_forecast"
    try:
        app_dir.mkdir(parents=True, exist_ok=True)
        user_db = app_dir / "alerts_data.db"
    except Exception:
        user_db = cwd_db

    if not user_db.exists():
        bundled_seed = None
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            candidate = Path(sys._MEIPASS) / "alerts_data.db"
            if candidate.exists():
                bundled_seed = candidate
        else:
            candidate = Path(__file__).resolve().parent.parent / "alerts_data.db"
            if candidate.exists():
                bundled_seed = candidate

        if bundled_seed and bundled_seed.exists():
            try:
                shutil.copy2(bundled_seed, user_db)
            except Exception:
                pass

    return user_db

DB_PATH = _get_app_db_path()

def _init_db_sync():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_id TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                duration_minutes REAL,
                source_channel TEXT,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                is_partial INTEGER DEFAULT 0,
                sub_regions_json TEXT DEFAULT '[]'
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS threat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                is_clear INTEGER NOT NULL,
                region_ids TEXT,
                sub_regions_json TEXT,
                confidence REAL,
                direction TEXT,
                created_at TEXT NOT NULL
            );
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_alerts_region ON alerts(region_id);")
        db.execute("CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active);")
        db.execute("CREATE INDEX IF NOT EXISTS idx_logs_created ON threat_logs(created_at);")

        db.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                username TEXT PRIMARY KEY,
                region_id TEXT DEFAULT 'UA-32',
                is_subscribed INTEGER DEFAULT 0,
                subscribed_channels TEXT DEFAULT '[]',
                updated_at TEXT NOT NULL
            );
        """)

        # Automatic schema migrations
        try:
            db.execute("ALTER TABLE alerts ADD COLUMN is_partial INTEGER DEFAULT 0;")
        except Exception:
            pass
        try:
            db.execute("ALTER TABLE alerts ADD COLUMN alert_level TEXT DEFAULT 'RED';")
        except Exception:
            pass
        try:
            db.execute("ALTER TABLE alerts ADD COLUMN sub_regions_json TEXT DEFAULT '[]';")
        except Exception:
            pass
        try:
            db.execute("ALTER TABLE threat_logs ADD COLUMN sub_regions_json TEXT DEFAULT '[]';")
        except Exception:
            pass

        db.commit()

async def init_db():
    await asyncio.to_thread(_init_db_sync)

def _save_threat_log_sync(channel: str, raw_text: str, threat_type: str, is_clear: bool, region_ids: List[str], sub_regions: List[Dict[str, Any]], confidence: float, direction: Optional[str]):
    now_iso = datetime.now(timezone.utc).isoformat()
    sub_json = json.dumps(sub_regions)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            INSERT INTO threat_logs (channel, raw_text, threat_type, is_clear, region_ids, sub_regions_json, confidence, direction, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (channel, raw_text, threat_type, 1 if is_clear else 0, ",".join(region_ids), sub_json, confidence, direction, now_iso))
        db.commit()

async def save_threat_log(
    channel: str,
    raw_text: str,
    threat_type: str,
    is_clear: bool,
    region_ids: List[str],
    sub_regions: List[Dict[str, Any]],
    confidence: float,
    direction: Optional[str] = None
):
    await asyncio.to_thread(_save_threat_log_sync, channel, raw_text, threat_type, is_clear, region_ids, sub_regions, confidence, direction)

LEVEL_PRIORITY: Dict[str, int] = {
    "RED": 3,
    "ORANGE": 2,
    "YELLOW": 1,
    "CLEAR": 0
}

def _activate_alert_sync(region_id: str, threat_type: str, source_channel: str, description: str, is_partial: bool = False, sub_regions: Optional[List[Dict[str, Any]]] = None, alert_level: Optional[str] = None):
    now_iso = datetime.now(timezone.utc).isoformat()
    sub_json = json.dumps(sub_regions or [])

    level = alert_level
    if not level:
        try:
            level = THREAT_TO_ALERT_LEVEL.get(ThreatType(threat_type), AlertLevel.YELLOW).value
        except Exception:
            level = "YELLOW"

    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute("SELECT id, is_partial, alert_level, threat_type, source_channel FROM alerts WHERE region_id = ? AND is_active = 1", (region_id,))
        row = cursor.fetchone()
        if not row:
            db.execute("""
                INSERT INTO alerts (region_id, threat_type, started_at, source_channel, description, is_active, is_partial, sub_regions_json, alert_level)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (region_id, threat_type, now_iso, source_channel, description, 1 if is_partial else 0, sub_json, level))
            db.commit()
        else:
            alert_id, existing_partial, existing_level, existing_threat, existing_source = row
            
            # If incoming call is generic telemetry confirmation from open siren API:
            if source_channel == "Офіційна Телеметрія Тривог":
                # If existing is generic or its level differs from newly evaluated siren level:
                if existing_threat == ThreatType.GENERAL_ALERT.value or existing_source == "Офіційна Телеметрія Тривог":
                    if existing_level != level or existing_threat != threat_type:
                        db.execute("UPDATE alerts SET alert_level = ?, threat_type = ? WHERE id = ?", (level, threat_type, alert_id))
                        db.commit()
                return

            # Incoming call is from concrete threat intelligence (Telegram / AF / Radar)
            updates = []
            params = []

            # 1. Update threat_type, source, description, and alert_level
            updates.append("threat_type = ?")
            params.append(threat_type)
            updates.append("source_channel = ?")
            params.append(source_channel)
            updates.append("description = ?")
            params.append(description)
            updates.append("alert_level = ?")
            params.append(level)

            # 2. Update sub-regions & partial state if provided
            if sub_regions:
                updates.append("sub_regions_json = ?")
                params.append(sub_json)
                updates.append("is_partial = ?")
                params.append(1 if is_partial else 0)
            elif not is_partial and existing_partial:
                updates.append("is_partial = 0")

            if updates:
                params.append(alert_id)
                db.execute(f"UPDATE alerts SET {', '.join(updates)} WHERE id = ?", tuple(params))
                db.commit()

async def activate_alert(region_id: str, threat_type: str, source_channel: str, description: str, is_partial: bool = False, sub_regions: Optional[List[Dict[str, Any]]] = None, alert_level: Optional[str] = None):
    await asyncio.to_thread(_activate_alert_sync, region_id, threat_type, source_channel, description, is_partial, sub_regions, alert_level)

def _clear_alert_sync(region_id: str):
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute("SELECT id, started_at FROM alerts WHERE region_id = ? AND is_active = 1", (region_id,))
        rows = cursor.fetchall()
        for row in rows:
            alert_id, started_at_str = row[0], row[1]
            try:
                started_at = datetime.fromisoformat(started_at_str)
                dur_min = (now - started_at).total_seconds() / 60.0
            except Exception:
                dur_min = 30.0
            db.execute("""
                UPDATE alerts SET is_active = 0, finished_at = ?, duration_minutes = ?
                WHERE id = ?
            """, (now_iso, dur_min, alert_id))
        db.commit()

async def clear_alert(region_id: str):
    await asyncio.to_thread(_clear_alert_sync, region_id)

def _get_active_alerts_sync() -> Dict[str, Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cursor = db.execute("SELECT * FROM alerts WHERE is_active = 1")
        rows = cursor.fetchall()
        result = {}
        for r in rows:
            d = dict(r)
            try:
                d["sub_regions"] = json.loads(d.get("sub_regions_json") or "[]")
            except Exception:
                d["sub_regions"] = []
            result[r["region_id"]] = d
        return result

async def get_active_alerts() -> Dict[str, Dict[str, Any]]:
    return await asyncio.to_thread(_get_active_alerts_sync)

def _get_recent_threat_logs_sync(limit: int = 50) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cursor = db.execute("SELECT * FROM threat_logs ORDER BY id DESC LIMIT ?", (limit,))
        res = []
        for r in cursor.fetchall():
            d = dict(r)
            try:
                d["sub_regions"] = json.loads(d.get("sub_regions_json") or "[]")
            except Exception:
                d["sub_regions"] = []
            res.append(d)
        return res

async def get_recent_threat_logs(limit: int = 50) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_recent_threat_logs_sync, limit)

def _get_recent_alerts_history_sync(limit: int = 100) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cursor = db.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]

async def get_recent_alerts_history(limit: int = 100) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_recent_alerts_history_sync, limit)

def _save_user_profile_sync(username: str, region_id: str = "UA-32", is_subscribed: bool = False, channels: Optional[List[str]] = None) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    ch_json = json.dumps(channels or [])
    clean_user = username.strip().lstrip('@')
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            INSERT INTO user_profiles (username, region_id, is_subscribed, subscribed_channels, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                region_id = excluded.region_id,
                is_subscribed = excluded.is_subscribed,
                subscribed_channels = excluded.subscribed_channels,
                updated_at = excluded.updated_at
        """, (clean_user, region_id, 1 if is_subscribed else 0, ch_json, now_iso))
        db.commit()
    return {
        "username": clean_user,
        "region_id": region_id,
        "is_subscribed": is_subscribed,
        "subscribed_channels": channels or [],
        "updated_at": now_iso
    }

async def save_user_profile(username: str, region_id: str = "UA-32", is_subscribed: bool = False, channels: Optional[List[str]] = None) -> Dict[str, Any]:
    return await asyncio.to_thread(_save_user_profile_sync, username, region_id, is_subscribed, channels)

def _get_user_profile_sync(username: str) -> Optional[Dict[str, Any]]:
    clean_user = username.strip().lstrip('@')
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cur = db.execute("SELECT * FROM user_profiles WHERE username = ?", (clean_user,))
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["subscribed_channels"] = json.loads(d.get("subscribed_channels") or "[]")
        except Exception:
            d["subscribed_channels"] = []
        d["is_subscribed"] = bool(d.get("is_subscribed", 0))
        return d

async def get_user_profile(username: str) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_user_profile_sync, username)
