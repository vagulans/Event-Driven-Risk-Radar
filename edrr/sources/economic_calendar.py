from datetime import datetime, timedelta
from typing import List
import uuid

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


class EconomicCalendarSource(EventSource):
    """Event source for major economic calendar events (FOMC, CPI, NFP, GDP)."""

    ECONOMIC_EVENTS = [
        {"name": "FOMC Rate Decision", "impact_hours": 4},
        {"name": "CPI Release", "impact_hours": 3},
        {"name": "Non-Farm Payrolls", "impact_hours": 3},
        {"name": "GDP Release", "impact_hours": 2},
        {"name": "FOMC Minutes", "impact_hours": 2},
        {"name": "PCE Inflation", "impact_hours": 2},
        {"name": "Retail Sales", "impact_hours": 1},
        {"name": "Jobless Claims", "impact_hours": 1},
    ]

    AFFECTED_ASSETS = ["SPY", "QQQ", "BTC", "GOLD"]

    async def fetch_events(self) -> List[Event]:
        """Fetch scheduled economic calendar events.
        
        Returns:
            List of Tier 1 economic events with appropriate impact windows.
        """
        events: List[Event] = []
        now = datetime.now()

        for event_info in self.ECONOMIC_EVENTS:
            event = Event(
                id=f"econ-{uuid.uuid4().hex[:8]}",
                title=event_info["name"],
                category=EventCategory.ECONOMIC,
                tier=EventTier.TIER_1,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=event_info["impact_hours"]),
                affected_assets=self.AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        return events

    def get_source_name(self) -> str:
        """Get the name of this event source."""
        return "Economic Calendar"
