from datetime import datetime, timedelta
from typing import List, Tuple
import uuid

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


class FedCalendarSource(EventSource):
    """Event source for Federal Reserve speaker schedules."""

    FED_SPEAKERS: List[Tuple[str, float]] = [
        ("Fed Chair Powell", 2),
        ("Fed Vice Chair", 1.5),
        ("NY Fed President", 1.5),
        ("Fed Governor Waller", 1),
        ("Fed Governor Bowman", 1),
        ("Fed Governor Cook", 1),
        ("Fed Governor Kugler", 1),
        ("Fed Governor Jefferson", 1),
        ("Regional Fed President", 1),
    ]

    AFFECTED_ASSETS = ["SPY", "QQQ", "BTC", "GOLD"]

    async def fetch_events(self) -> List[Event]:
        """Fetch Federal Reserve speaker events.
        
        Returns:
            List of Tier 2 Fed speaker events with 1-2 hour impact windows.
        """
        events: List[Event] = []
        now = datetime.now()

        for name, impact_hours in self.FED_SPEAKERS:
            event = Event(
                id=f"fed-{uuid.uuid4().hex[:8]}",
                title=f"{name} Speech",
                category=EventCategory.FED_SPEAKER,
                tier=EventTier.TIER_2,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=impact_hours),
                affected_assets=self.AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        return events

    def get_source_name(self) -> str:
        """Get the name of this event source."""
        return "Fed Calendar"
