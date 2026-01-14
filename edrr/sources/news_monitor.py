from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid

import aiohttp

from edrr.models.events import Event, EventCategory, EventTier
from edrr.sources.base import EventSource


EMERGING_KEYWORDS = {
    "geopolitical": [
        "war", "invasion", "military", "sanctions", "tariff", "trade war",
        "conflict", "nuclear", "missile", "attack", "terrorism", "coup",
    ],
    "presidential": [
        "president", "executive order", "white house", "oval office",
        "presidential address", "state of the union", "emergency declaration",
    ],
    "regulatory": [
        "sec", "cftc", "fed", "federal reserve", "treasury", "regulation",
        "enforcement", "investigation", "subpoena", "lawsuit", "antitrust",
    ],
}

IMPACT_HOURS_BY_CATEGORY = {
    EventCategory.GEOPOLITICAL: 24,
    EventCategory.REGULATORY: 12,
}

DEFAULT_IMPACT_HOURS = 6


class NewsMonitorSource(EventSource):
    """Event source that monitors news feeds for emerging Tier 3 events.
    
    Handles unscheduled events including:
    - Geopolitical events (conflicts, sanctions, trade wars)
    - Unscheduled presidential announcements
    - Regulatory actions and investigations
    """

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key
        self.api_url = api_url or "https://newsapi.org/v2/top-headlines"

    async def fetch_events(self) -> List[Event]:
        """Fetch emerging events from news API feeds.
        
        Returns:
            List of Event objects for detected emerging events.
        """
        events: List[Event] = []
        
        articles = await self._poll_news_api()
        
        for article in articles:
            event = self._classify_article(article)
            if event:
                events.append(event)
        
        return events

    def get_source_name(self) -> str:
        return "News Monitor"

    async def _poll_news_api(self) -> List[Dict[str, Any]]:
        """Poll news API for latest articles.
        
        Returns:
            List of article dictionaries from the news API.
        """
        if not self.api_key:
            return []
        
        params = {
            "apiKey": self.api_key,
            "category": "business",
            "country": "us",
            "pageSize": 50,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("articles", [])
                    return []
        except aiohttp.ClientError:
            return []

    def _classify_article(self, article: Dict[str, Any]) -> Optional[Event]:
        """Classify a news article and create an Event if relevant.
        
        Args:
            article: Article dictionary from news API.
            
        Returns:
            Event object if article is classified as market-moving, None otherwise.
        """
        title = article.get("title", "").lower()
        description = article.get("description", "").lower() if article.get("description") else ""
        content = f"{title} {description}"
        
        category = self._detect_category(content)
        if not category:
            return None
        
        impact_hours = IMPACT_HOURS_BY_CATEGORY.get(category, DEFAULT_IMPACT_HOURS)
        
        published_at = article.get("publishedAt")
        if published_at:
            try:
                scheduled_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                scheduled_time = datetime.utcnow()
        else:
            scheduled_time = datetime.utcnow()
        
        affected_assets = self._determine_affected_assets(category, content)
        
        return Event(
            id=f"news-{uuid.uuid4().hex[:8]}",
            title=article.get("title", "Unknown News Event"),
            category=category,
            tier=EventTier.TIER_3,
            scheduled_time=scheduled_time,
            impact_window=timedelta(hours=impact_hours),
            affected_assets=affected_assets,
        )

    def _detect_category(self, content: str) -> Optional[EventCategory]:
        """Detect the event category based on content keywords.
        
        Args:
            content: Combined title and description text.
            
        Returns:
            EventCategory if detected, None otherwise.
        """
        for keyword in EMERGING_KEYWORDS["geopolitical"]:
            if keyword in content:
                return EventCategory.GEOPOLITICAL
        
        for keyword in EMERGING_KEYWORDS["presidential"]:
            if keyword in content:
                return EventCategory.GEOPOLITICAL
        
        for keyword in EMERGING_KEYWORDS["regulatory"]:
            if keyword in content:
                return EventCategory.REGULATORY
        
        return None

    def _determine_affected_assets(self, category: EventCategory, content: str) -> List[str]:
        """Determine which assets are affected by this event.
        
        Args:
            category: The event category.
            content: Combined title and description text.
            
        Returns:
            List of affected asset symbols.
        """
        assets = ["SPY", "QQQ"]
        
        if category == EventCategory.GEOPOLITICAL:
            assets.extend(["BTC", "GOLD"])
        
        if category == EventCategory.REGULATORY:
            if "crypto" in content or "bitcoin" in content or "digital asset" in content:
                assets.append("BTC")
            assets.append("GOLD")
        
        if "gold" in content or "precious metal" in content:
            if "GOLD" not in assets:
                assets.append("GOLD")
        
        if "bitcoin" in content or "crypto" in content:
            if "BTC" not in assets:
                assets.append("BTC")
        
        return list(set(assets))
