from datetime import datetime, timedelta
from typing import List
import uuid

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


class EarningsCalendarSource(EventSource):
    """Event source for mega-cap earnings schedules."""

    HIGH_IMPACT_TICKERS = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "GOOGL", "name": "Alphabet Inc."},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "META", "name": "Meta Platforms Inc."},
    ]

    IMPACT_HOURS = 14

    async def fetch_events(self) -> List[Event]:
        """Fetch scheduled mega-cap earnings events.
        
        Returns:
            List of Tier 1 earnings events filtered to high-impact names.
            Impact window covers after-hours + next morning trading.
        """
        events: List[Event] = []
        now = datetime.now()

        for ticker in self.HIGH_IMPACT_TICKERS:
            affected_assets = ["SPY", "QQQ"]
            if ticker["symbol"] in ("NVDA", "TSLA"):
                affected_assets.append("BTC")

            event = Event(
                id=f"earn-{ticker['symbol'].lower()}-{uuid.uuid4().hex[:8]}",
                title=f"{ticker['symbol']} Earnings - {ticker['name']}",
                category=EventCategory.EARNINGS,
                tier=EventTier.TIER_1,
                scheduled_time=now + timedelta(days=1),
                impact_window=timedelta(hours=self.IMPACT_HOURS),
                affected_assets=affected_assets,
            )
            events.append(event)

        return events

    def get_source_name(self) -> str:
        """Get the name of this event source."""
        return "Earnings Calendar"
