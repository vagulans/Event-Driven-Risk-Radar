from datetime import datetime, timedelta
from typing import Callable, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from edrr.models.config import Config
from edrr.models.events import Event


class Scheduler:
    def __init__(
        self,
        config: Optional[Config] = None,
        on_calendar_poll: Optional[Callable] = None,
        on_news_monitor: Optional[Callable] = None,
        on_risk_recalculate: Optional[Callable] = None,
    ) -> None:
        self.config = config or Config()
        self._scheduler = AsyncIOScheduler()
        self._on_calendar_poll = on_calendar_poll
        self._on_news_monitor = on_news_monitor
        self._on_risk_recalculate = on_risk_recalculate
        self._events: List[Event] = []
        self._risk_recalc_job_id = "risk_recalculate"

    def set_events(self, events: List[Event]) -> None:
        self._events = events

    def start(self) -> None:
        if self._on_calendar_poll:
            self._scheduler.add_job(
                self._on_calendar_poll,
                IntervalTrigger(hours=1),
                id="calendar_poll",
                replace_existing=True,
            )

        if self._on_news_monitor:
            self._scheduler.add_job(
                self._on_news_monitor,
                IntervalTrigger(minutes=5),
                id="news_monitor",
                replace_existing=True,
            )

        if self._on_risk_recalculate:
            self._scheduler.add_job(
                self._check_and_recalculate_risk,
                IntervalTrigger(minutes=1),
                id=self._risk_recalc_job_id,
                replace_existing=True,
            )

        self._scheduler.start()

    def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def is_running(self) -> bool:
        return self._scheduler.running

    async def _check_and_recalculate_risk(self) -> None:
        if not self._on_risk_recalculate:
            return

        now = datetime.now()
        threshold = timedelta(hours=2)

        has_imminent_event = any(
            timedelta(0) <= (event.scheduled_time - now) <= threshold
            for event in self._events
        )

        if has_imminent_event:
            await self._on_risk_recalculate()

    async def trigger_calendar_poll(self) -> None:
        if self._on_calendar_poll:
            await self._on_calendar_poll()

    async def trigger_news_monitor(self) -> None:
        if self._on_news_monitor:
            await self._on_news_monitor()

    async def trigger_risk_recalculate(self) -> None:
        if self._on_risk_recalculate:
            await self._on_risk_recalculate()
