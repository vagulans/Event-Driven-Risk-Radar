from datetime import datetime, timedelta
from typing import List
import uuid

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


class CryptoEventsSource(EventSource):
    """Event source for crypto-specific events (protocol upgrades, token unlocks, SEC ETF deadlines)."""

    CRYPTO_EVENTS = [
        {"name": "Bitcoin Halving", "impact_hours": 48, "category": EventCategory.CRYPTO},
        {"name": "Ethereum Protocol Upgrade", "impact_hours": 24, "category": EventCategory.CRYPTO},
        {"name": "Major Token Unlock", "impact_hours": 12, "category": EventCategory.CRYPTO},
        {"name": "Exchange Maintenance", "impact_hours": 6, "category": EventCategory.CRYPTO},
        {"name": "Stablecoin Audit Report", "impact_hours": 8, "category": EventCategory.CRYPTO},
    ]

    REGULATORY_EVENTS = [
        {"name": "SEC ETF Decision Deadline", "impact_hours": 24, "category": EventCategory.REGULATORY},
        {"name": "SEC Enforcement Action", "impact_hours": 12, "category": EventCategory.REGULATORY},
        {"name": "CFTC Regulatory Announcement", "impact_hours": 8, "category": EventCategory.REGULATORY},
        {"name": "Congressional Crypto Hearing", "impact_hours": 4, "category": EventCategory.REGULATORY},
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

        for event_info in self.CRYPTO_EVENTS:
            event = Event(
                id=f"crypto-{uuid.uuid4().hex[:8]}",
                title=event_info["name"],
                category=event_info["category"],
                tier=EventTier.TIER_4,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=event_info["impact_hours"]),
                affected_assets=self.AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        for event_info in self.REGULATORY_EVENTS:
            event = Event(
                id=f"reg-{uuid.uuid4().hex[:8]}",
                title=event_info["name"],
                category=event_info["category"],
                tier=EventTier.TIER_4,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=event_info["impact_hours"]),
                affected_assets=self.REGULATORY_AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        return events

    def get_source_name(self) -> str:
        """Get the name of this event source."""
        return "Crypto Events"
