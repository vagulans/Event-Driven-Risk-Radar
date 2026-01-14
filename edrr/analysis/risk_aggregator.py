from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from edrr.models.config import Config
from edrr.models.events import AssetRisk, Event, RiskWindow
from edrr.analysis.impact_scorer import ImpactScorer


@dataclass
class ClusterInfo:
    window_start: datetime
    window_end: datetime
    events: List[Event]
    compound_risk: int
    assets_affected: List[str]


class RiskAggregator:
    DEFAULT_ASSETS = ["SPY", "QQQ", "BTC", "GOLD"]
    
    def __init__(
        self,
        config: Optional[Config] = None,
        impact_scorer: Optional[ImpactScorer] = None,
    ) -> None:
        self.config = config or Config()
        self.impact_scorer = impact_scorer or ImpactScorer(self.config)
        self.events: List[Event] = []

    def set_events(self, events: List[Event]) -> None:
        self.events = events

    def get_current_risk(
        self,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, AssetRisk]:
        current_time = current_time or datetime.now()
        results: Dict[str, AssetRisk] = {}

        for asset in self.DEFAULT_ASSETS:
            max_score = 0
            next_event: Optional[Event] = None
            next_event_time: Optional[datetime] = None

            for event in self.events:
                if asset not in event.affected_assets:
                    continue

                score = self.impact_scorer.calculate_score(event, asset, current_time)
                if score > max_score:
                    max_score = score

                if event.scheduled_time > current_time:
                    if next_event_time is None or event.scheduled_time < next_event_time:
                        next_event_time = event.scheduled_time
                        next_event = event

            status = self._get_status_for_score(max_score)
            results[asset] = AssetRisk(
                asset=asset,
                score=max_score,
                status=status,
                next_event=next_event,
            )

        return results

    def detect_clustering(
        self,
        current_time: Optional[datetime] = None,
        lookhead_hours: int = 24,
        window_hours: int = 2,
    ) -> List[ClusterInfo]:
        current_time = current_time or datetime.now()
        end_time = current_time + timedelta(hours=lookhead_hours)
        clusters: List[ClusterInfo] = []

        relevant_events = [
            e for e in self.events
            if current_time <= e.scheduled_time <= end_time
        ]

        if not relevant_events:
            return clusters

        relevant_events.sort(key=lambda e: e.scheduled_time)

        checked: set = set()
        for event in relevant_events:
            if event.id in checked:
                continue

            window_start = event.scheduled_time
            window_end = window_start + timedelta(hours=window_hours)
            events_in_window = [
                e for e in relevant_events
                if window_start <= e.scheduled_time <= window_end
            ]

            if len(events_in_window) >= 2:
                for e in events_in_window:
                    checked.add(e.id)

                assets_affected = list(
                    set(a for e in events_in_window for a in e.affected_assets)
                )
                compound_risk = self._calculate_compound_risk(events_in_window)
                clusters.append(
                    ClusterInfo(
                        window_start=window_start,
                        window_end=window_end,
                        events=events_in_window,
                        compound_risk=compound_risk,
                        assets_affected=assets_affected,
                    )
                )

        return clusters

    def get_danger_zones(
        self,
        current_time: Optional[datetime] = None,
    ) -> Dict[str, List[RiskWindow]]:
        current_time = current_time or datetime.now()
        zones: Dict[str, List[RiskWindow]] = {
            "intraday": [],
            "high_risk_days": [],
            "high_risk_weeks": [],
        }

        zones["intraday"] = self._get_intraday_windows(current_time)
        zones["high_risk_days"] = self._get_high_risk_days(current_time)
        zones["high_risk_weeks"] = self._get_high_risk_weeks(current_time)

        return zones

    def _get_intraday_windows(self, current_time: datetime) -> List[RiskWindow]:
        windows: List[RiskWindow] = []
        end_of_day = current_time.replace(hour=23, minute=59, second=59)

        for event in self.events:
            if current_time <= event.scheduled_time <= end_of_day:
                window_start = event.scheduled_time - timedelta(minutes=30)
                window_end = event.scheduled_time + event.impact_window
                risk_level = self._calculate_event_risk_level(event)

                if risk_level >= self.config.risk_thresholds.elevated:
                    windows.append(
                        RiskWindow(
                            start_time=max(window_start, current_time),
                            end_time=window_end,
                            level=risk_level,
                            events=[event],
                            assets=event.affected_assets,
                        )
                    )

        return windows

    def _get_high_risk_days(self, current_time: datetime) -> List[RiskWindow]:
        windows: List[RiskWindow] = []
        end_of_week = current_time + timedelta(days=7)
        
        daily_events: Dict[str, List[Event]] = {}
        for event in self.events:
            if current_time <= event.scheduled_time <= end_of_week:
                day_key = event.scheduled_time.strftime("%Y-%m-%d")
                if day_key not in daily_events:
                    daily_events[day_key] = []
                daily_events[day_key].append(event)

        for day_key, events in daily_events.items():
            daily_risk = self._calculate_compound_risk(events)
            if daily_risk >= self.config.risk_thresholds.high:
                day_start = datetime.strptime(day_key, "%Y-%m-%d")
                day_end = day_start.replace(hour=23, minute=59, second=59)
                all_assets = list(set(a for e in events for a in e.affected_assets))
                windows.append(
                    RiskWindow(
                        start_time=day_start,
                        end_time=day_end,
                        level=daily_risk,
                        events=events,
                        assets=all_assets,
                    )
                )

        return windows

    def _get_high_risk_weeks(self, current_time: datetime) -> List[RiskWindow]:
        windows: List[RiskWindow] = []
        end_of_month = current_time + timedelta(days=30)

        week_start = current_time
        while week_start < end_of_month:
            week_end = week_start + timedelta(days=7)
            week_events = [
                e for e in self.events
                if week_start <= e.scheduled_time < week_end
            ]

            if week_events:
                weekly_risk = self._calculate_compound_risk(week_events)
                if weekly_risk >= self.config.risk_thresholds.danger:
                    all_assets = list(set(a for e in week_events for a in e.affected_assets))
                    windows.append(
                        RiskWindow(
                            start_time=week_start,
                            end_time=week_end,
                            level=weekly_risk,
                            events=week_events,
                            assets=all_assets,
                        )
                    )

            week_start = week_end

        return windows

    def _get_status_for_score(self, score: int) -> str:
        thresholds = self.config.risk_thresholds
        if score >= thresholds.danger:
            return "danger"
        elif score >= thresholds.high:
            return "high"
        elif score >= thresholds.elevated:
            return "elevated"
        elif score >= thresholds.low:
            return "low"
        else:
            return "normal"

    def _calculate_event_risk_level(self, event: Event) -> int:
        max_score = 0
        for asset in event.affected_assets:
            score = self.impact_scorer.calculate_score(event, asset)
            max_score = max(max_score, score)
        return max_score

    def _calculate_compound_risk(self, events: List[Event]) -> int:
        if not events:
            return 0

        max_base = 0
        for event in events:
            base_score = self._calculate_event_risk_level(event)
            max_base = max(max_base, base_score)

        cluster_bonus = min(3, len(events) - 1)
        compound = min(10, max_base + cluster_bonus)
        return compound
