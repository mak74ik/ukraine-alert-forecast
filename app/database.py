"""
Resilient SQLite database for storing alerts, threat logs, and empirical distributions.
Supports sub-regional granularity, localized districts, and fail-safe recovery.
"""
import sqlite3
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path("alerts_data.db")

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

        # Automatic schema migrations
        try:
            db.execute("ALTER TABLE alerts ADD COLUMN is_partial INTEGER DEFAULT 0;")
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

def _activate_alert_sync(region_id: str, threat_type: str, source_channel: str, description: str, is_partial: bool = False, sub_regions: Optional[List[Dict[str, Any]]] = None):
    now_iso = datetime.now(timezone.utc).isoformat()
    sub_json = json.dumps(sub_regions or [])
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute("SELECT id, is_partial FROM alerts WHERE region_id = ? AND is_active = 1", (region_id,))
        row = cursor.fetchone()
        if not row:
            db.execute("""
                INSERT INTO alerts (region_id, threat_type, started_at, source_channel, description, is_active, is_partial, sub_regions_json)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (region_id, threat_type, now_iso, source_channel, description, 1 if is_partial else 0, sub_json))
            db.commit()
        else:
            # If incoming is full alert, upgrade from partial
            if not is_partial:
                db.execute("UPDATE alerts SET is_partial = 0 WHERE id = ?", (row[0],))
                db.commit()

async def activate_alert(region_id: str, threat_type: str, source_channel: str, description: str, is_partial: bool = False, sub_regions: Optional[List[Dict[str, Any]]] = None):
    await asyncio.to_thread(_activate_alert_sync, region_id, threat_type, source_channel, description, is_partial, sub_regions)

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
