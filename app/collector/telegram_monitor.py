"""
Autonomous Telegram & Open Source Ingestion Engine.
Connects via Telethon if credentials exist, with robust autonomous simulation fallback.
"""
import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Optional, List, Callable, Dict, Any

from app.config import settings
from app.collector.parser import LocalThreatParser, ThreatEvent
from app.collector.threat_types import ThreatType
from app.database import save_threat_log, activate_alert, clear_alert, get_active_alerts
from app.engine.trajectory import project_threat_trajectory, ThreatProjection

logger = logging.getLogger("telegram_monitor")

# Realistic sample events for autonomous live simulator
SAMPLE_TELEGRAM_MESSAGES = [
    {
        "channel": "kpszsu",
        "text": "🔴 Увага! Зафіксовано зліт кількох бортів МіГ-31К з аеродрому Саваслейка! Ракетна небезпека по всій території України!",
    },
    {
        "channel": "vanek_nikolaev",
        "text": "Група «Шахедів» з Чорного моря заходить на південь Одеської області! Курс на Затоку / Білгород-Дністровський!",
    },
    {
        "channel": "air_alert_ua",
        "text": "🟢 Відбій повітряної тривоги в Одеській та Миколаївській областях.",
    },
    {
        "channel": "kpszsu",
        "text": "⚠️ Загроза застосування балістичного озброєння з північно-східного напрямку! Харківська, Сумська, Полтавська області — в укриття!",
    },
    {
        "channel": "radarradar_ua",
        "text": "БПЛА Shahed курсом через Сумщину в напрямку Полтавщини та Черкащини!",
    },
    {
        "channel": "kpszsu",
        "text": "Пуски керованих авіаційних бомб (КАБ) тактичною авіацією на Запоріжжі та Донеччині!",
    },
    {
        "channel": "vanek_nikolaev",
        "text": "🟢 Відбій загрози по МіГ-31К по всіх областях. Посадка бортів.",
    },
    {
        "channel": "kpszsu",
        "text": "БПЛА на межі Вінницької та Хмельницької областей, курс на Старокостянтинів!",
    }
]

class TelegramMonitoringService:
    def __init__(self, on_event_callback: Optional[Callable[[ThreatEvent, List[ThreatProjection]], Any]] = None):
        self.parser = LocalThreatParser()
        self.on_event_callback = on_event_callback
        self.active_projections: List[ThreatProjection] = []
        self._running = False
        self._telethon_client = None

    async def start(self):
        self._running = True
        
        # Check if real Telethon credentials are provided
        if settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH:
            logger.info("Initializing Telethon client for live Telegram channels...")
            asyncio.create_task(self._run_telethon())
        else:
            logger.info("Telegram API credentials not configured. Starting autonomous background data feeder...")
            asyncio.create_task(self._run_autonomous_simulation_loop())

    async def stop(self):
        self._running = False
        if self._telethon_client:
            await self._telethon_client.disconnect()

    async def process_raw_message(self, text: str, channel: str = "custom_feed", timestamp: Optional[datetime] = None) -> Optional[ThreatEvent]:
        """Process incoming raw message through zero-LLM local parser and update state."""
        event = self.parser.parse_message(text, channel=channel, msg_time=timestamp)
        if not event:
            return None

        # Save to DB log
        await save_threat_log(
            channel=channel,
            raw_text=text,
            threat_type=event.threat_type.value,
            is_clear=event.is_clear,
            region_ids=event.region_ids,
            confidence=event.confidence,
            direction=event.direction
        )

        # Update database alert statuses
        new_projections: List[ThreatProjection] = []
        if event.is_clear or event.threat_type == ThreatType.ALL_CLEAR:
            for reg_id in event.region_ids:
                await clear_alert(reg_id)
            # Filter out cleared region projections
            self.active_projections = [p for p in self.active_projections if p.target_region_id not in event.region_ids]
        else:
            for reg_id in event.region_ids:
                await activate_alert(
                    region_id=reg_id,
                    threat_type=event.threat_type.value,
                    source_channel=channel,
                    description=text[:200]
                )
                # Compute spatial kinematic projections if Shahed or Cruise Missile
                if event.threat_type in (ThreatType.SHAHED, ThreatType.SEA_CRUISE, ThreatType.STRATEGIC_AVIATION):
                    projs = project_threat_trajectory(
                        origin_region_id=reg_id,
                        threat_type=event.threat_type,
                        start_time=event.timestamp,
                        direction=event.direction
                    )
                    new_projections.extend(projs)

            # Update active projections list
            self.active_projections.extend(new_projections)
            # Prune expired projections (> 3 hours old)
            now = datetime.now(timezone.utc)
            self.active_projections = [p for p in self.active_projections if (now - p.eta_start).total_seconds() < 10800]

        if self.on_event_callback:
            try:
                res = self.on_event_callback(event, new_projections)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as e:
                logger.error(f"Callback error: {e}")

        return event

    async def _run_telethon(self):
        """Telethon real-time scraper."""
        try:
            from telethon import TelegramClient, events
            self._telethon_client = TelegramClient('ua_alerts_session', settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
            await self._telethon_client.start(phone=settings.TELEGRAM_PHONE)
            
            logger.info("Connected to Telegram successfully!")

            @self._telethon_client.on(events.NewMessage(chats=settings.TELEGRAM_CHANNELS))
            async def handler(event):
                sender = await event.get_chat()
                channel_name = getattr(sender, 'username', 'telegram') or 'telegram'
                await self.process_raw_message(event.text, channel=f"@{channel_name}", timestamp=event.date)

            await self._telethon_client.run_until_disconnected()
        except Exception as e:
            logger.warning(f"Telethon connection failed or cancelled: {e}. Switching to autonomous simulation engine.")
            await self._run_autonomous_simulation_loop()

    async def _run_autonomous_simulation_loop(self):
        """Generates continuous realistic monitoring alerts when running standalone."""
        # Initial seed of initial alerts
        await self.process_raw_message(SAMPLE_TELEGRAM_MESSAGES[1]["text"], channel="@vanek_nikolaev")
        await asyncio.sleep(2)
        await self.process_raw_message(SAMPLE_TELEGRAM_MESSAGES[3]["text"], channel="@kpszsu")

        while self._running:
            try:
                # Random interval between 25 and 60 seconds
                wait_sec = random.randint(25, 60)
                await asyncio.sleep(wait_sec)

                sample = random.choice(SAMPLE_TELEGRAM_MESSAGES)
                await self.process_raw_message(sample["text"], channel=f"@{sample['channel']}")
            except Exception as e:
                logger.error(f"Simulation loop error: {e}")
                await asyncio.sleep(10)
