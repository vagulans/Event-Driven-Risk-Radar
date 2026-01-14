from datetime import datetime, timedelta
from typing import List
import uuid

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


class FedCalendarSource(EventSource):
    """Event source for Federal Reserve speaker schedules."""

    FED_SPEAKERS = [
        {"name": "Fed Chair Powell", "impact_hours": 2},
        {"name": "Fed Vice Chair", "impact_hours": 1.5},
        {"name": "NY Fed President", "impact_hours": 1.5},
        {"name": "Fed Governor Waller", "impact_hours": 1},
        {"name": "Fed Governor Bowman", "impact_hours": 1},
        {"name": "Fed Governor Cook", "impact_hours": 1},
        {"name": "Fed Governor Kugler", "impact_hours": 1},
        {"name": "Fed Governor Jefferson", "impact_hours": 1},
        {"name": "Regional Fed President", "impact_hours": 1},
    ]

    AFFECTED_ASSETS = ["SPY", "QQQ", "BTC", "GOLD"]

    async def fetch_events(self) -> List[Event]:
        """Fetch Federal Reserve speaker events.
        
        Returns:
            List of Tier 2 Fed speaker events with 1-2 hour impact windows.
        """
        events: List[Event] = []
        now = datetime.now()

        for speaker_info in self.FED_SPEAKERS:
            event = Event(
                id=f"fed-{uuid.uuid4().hex[:8]}",
                title=f"{speaker_info['name']} Speech",
                category=EventCategory.FED_SPEAKER,
                tier=EventTier.TIER_2,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=speaker_info["impact_hours"]),
                affected_assets=self.AFFECTED_ASSETS.copy(),
            )
            events.append(event)

        return events

    def get_source_name(self) -> str:
        """Get the name of this event source."""
        return "Fed Calendar"
