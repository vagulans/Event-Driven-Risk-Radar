from datetime import datetime, timedelta
from typing import List, Tuple
import uuid

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


class EconomicCalendarSource(EventSource):
    """Event source for major economic calendar events (FOMC, CPI, NFP, GDP)."""

    ECONOMIC_EVENTS: List[Tuple[str, float]] = [
        ("FOMC Rate Decision", 4),
        ("CPI Release", 3),
        ("Non-Farm Payrolls", 3),
        ("GDP Release", 2),
        ("FOMC Minutes", 2),
        ("PCE Inflation", 2),
        ("Retail Sales", 1),
        ("Jobless Claims", 1),
    ]

    AFFECTED_ASSETS = ["SPY", "QQQ", "BTC", "GOLD"]

    async def fetch_events(self) -> List[Event]:
        """Fetch scheduled economic calendar events.
        
        Returns:
            List of Tier 1 economic events with appropriate impact windows.
        """
        events: List[Event] = []
        now = datetime.now()

        for name, impact_hours in self.ECONOMIC_EVENTS:
            event = Event(
                id=f"econ-{uuid.uuid4().hex[:8]}",
                title=name,
                category=EventCategory.ECONOMIC,
                tier=EventTier.TIER_1,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=impact_hours),
                affected_assets=self.AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        return events

    def get_source_name(self) -> str:
        """Get the name of this event source."""
        return "Economic Calendar"
