from datetime import datetime
from typing import Dict, List, Optional

from edrr.models.config import Config
from edrr.models.events import AssetRisk, Event
from edrr.sources.base import EventSource
from edrr.sources.economic_calendar import EconomicCalendarSource
from edrr.sources.fed_calendar import FedCalendarSource
from edrr.sources.earnings_calendar import EarningsCalendarSource
from edrr.sources.news_monitor import NewsMonitorSource
from edrr.sources.crypto_events import CryptoEventsSource
from edrr.analysis.impact_scorer import ImpactScorer
from edrr.analysis.risk_aggregator import RiskAggregator
from edrr.analysis.llm_client import LLMClient
from edrr.outputs.calendar_view import CalendarView
from edrr.outputs.alerts import AlertManager
from edrr.outputs.recommendations import RecommendationEngine
from edrr.scheduler import Scheduler


class RiskRadarEngine:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config()
        self._running = False
        self._events: List[Event] = []
        
        self._sources: List[EventSource] = [
            EconomicCalendarSource(),
            FedCalendarSource(),
            EarningsCalendarSource(),
            NewsMonitorSource(
                api_key=self.config.news_api_key,
                api_url="https://newsapi.org/v2/everything",
            ),
            CryptoEventsSource(),
        ]
        
        self.impact_scorer = ImpactScorer(self.config)
        self.risk_aggregator = RiskAggregator(self.config, self.impact_scorer)
        self.llm_client = LLMClient(api_key=self.config.anthropic_api_key)
        
        self.calendar_view = CalendarView(self.risk_aggregator, self.config)
        self.alert_manager = AlertManager(self.risk_aggregator, self.config)
        self.recommendation_engine = RecommendationEngine(self.config)
        
        self.scheduler = Scheduler(
            config=self.config,
            on_calendar_poll=self._on_calendar_poll,
            on_news_monitor=self._on_news_monitor,
            on_risk_recalculate=self._on_risk_recalculate,
        )

    async def start(self) -> None:
        if self._running:
            return
        
        await self._fetch_all_events()
        self.scheduler.start()
        self._running = True

    def stop(self) -> None:
        if not self._running:
            return
        
        self.scheduler.stop()
        self._running = False

    def is_running(self) -> bool:
        return self._running

    async def _fetch_all_events(self) -> None:
        all_events: List[Event] = []
        for source in self._sources:
            try:
                events = await source.fetch_events()
                all_events.extend(events)
            except Exception:
                pass
        
        self._events = all_events
        self.risk_aggregator.set_events(all_events)
        self.scheduler.set_events(all_events)

    async def _on_calendar_poll(self) -> None:
        await self._fetch_all_events()
        alerts = self.alert_manager.check_thresholds()
        for alert in alerts:
            self.alert_manager.send_alert(alert)

    async def _on_news_monitor(self) -> None:
        try:
            news_source = self._sources[3]
            new_events = await news_source.fetch_events()
            
            existing_ids = {e.id for e in self._events}
            for event in new_events:
                if event.id not in existing_ids:
                    self._events.append(event)
            
            self.risk_aggregator.set_events(self._events)
            self.scheduler.set_events(self._events)
            
            alerts = self.alert_manager.check_thresholds()
            for alert in alerts:
                self.alert_manager.send_alert(alert)
        except Exception:
            pass

    async def _on_risk_recalculate(self) -> None:
        alerts = self.alert_manager.check_thresholds()
        for alert in alerts:
            self.alert_manager.send_alert(alert)

    def get_status(
        self,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, AssetRisk]:
        return self.risk_aggregator.get_current_risk(current_time)

    def get_calendar_today(self, current_time: Optional[datetime] = None) -> str:
        return self.calendar_view.generate_today(current_time)

    def get_calendar_week(self, current_time: Optional[datetime] = None) -> str:
        return self.calendar_view.generate_week(current_time)

    def get_events(self) -> List[Event]:
        return self._events
