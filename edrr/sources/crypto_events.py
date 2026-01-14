from datetime import datetime, timedelta
from typing import List, Tuple
import uuid

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


class CryptoEventsSource(EventSource):
    """Event source for crypto-specific events (protocol upgrades, token unlocks, SEC ETF deadlines)."""

    CRYPTO_EVENTS: List[Tuple[str, float, EventCategory]] = [
        ("Bitcoin Halving", 48, EventCategory.CRYPTO),
        ("Ethereum Protocol Upgrade", 24, EventCategory.CRYPTO),
        ("Major Token Unlock", 12, EventCategory.CRYPTO),
        ("Exchange Maintenance", 6, EventCategory.CRYPTO),
        ("Stablecoin Audit Report", 8, EventCategory.CRYPTO),
    ]

    REGULATORY_EVENTS: List[Tuple[str, float, EventCategory]] = [
        ("SEC ETF Decision Deadline", 24, EventCategory.REGULATORY),
        ("SEC Enforcement Action", 12, EventCategory.REGULATORY),
        ("CFTC Regulatory Announcement", 8, EventCategory.REGULATORY),
        ("Congressional Crypto Hearing", 4, EventCategory.REGULATORY),
    ]

    AFFECTED_ASSETS = ["BTC", "ETH"]
    REGULATORY_AFFECTED_ASSETS = ["BTC", "ETH", "SPY", "QQQ"]

    async def fetch_events(self) -> List[Event]:
        """Fetch crypto-specific events including protocol upgrades, token unlocks, and regulatory events.
        
        Returns:
            List of Tier 4 crypto events and regulatory events with appropriate impact windows.
        """
        events: List[Event] = []
        now = datetime.now()

        for name, impact_hours, category in self.CRYPTO_EVENTS:
            event = Event(
                id=f"crypto-{uuid.uuid4().hex[:8]}",
                title=name,
                category=category,
                tier=EventTier.TIER_4,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=impact_hours),
                affected_assets=self.AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        for name, impact_hours, category in self.REGULATORY_EVENTS:
            event = Event(
                id=f"reg-{uuid.uuid4().hex[:8]}",
                title=name,
                category=category,
                tier=EventTier.TIER_4,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=impact_hours),
                affected_assets=self.REGULATORY_AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        return events

    def get_source_name(self) -> str:
        """Get the name of this event source."""
        return "Crypto Events"
