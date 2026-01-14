from datetime import datetime, timedelta
from typing import Dict, List, Optional

from edrr.models.config import Config
from edrr.models.events import Event, RiskWindow
from edrr.analysis.risk_aggregator import RiskAggregator


class CalendarView:
    RISK_LABELS = {
        (1, 3): "LOW",
        (4, 5): "MODERATE",
        (6, 7): "ELEVATED",
        (8, 9): "HIGH",
        (10, 10): "CRITICAL",
    }

    def __init__(
        self,
        risk_aggregator: Optional[RiskAggregator] = None,
        config: Optional[Config] = None,
    ) -> None:
        self.config = config or Config()
        self.risk_aggregator = risk_aggregator or RiskAggregator(self.config)

    def _get_risk_label(self, score: int) -> str:
        for (low, high), label in self.RISK_LABELS.items():
            if low <= score <= high:
                return label
        return "LOW"

    def _format_time_range(self, start: datetime, end: datetime) -> str:
        if start.date() == end.date():
            return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
        return f"{start.strftime('%H:%M')} - {end.strftime('%m/%d %H:%M')}"

    def _format_assets(self, assets: List[str]) -> str:
        if not assets:
            return ""
        if set(assets) >= {"SPY", "QQQ", "BTC", "GOLD"}:
            return "ALL"
        return ", ".join(assets)

    def _get_events_for_date(
        self,
        date: datetime,
        events: List[Event],
    ) -> List[Event]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return [
            e for e in events
            if start_of_day <= e.scheduled_time <= end_of_day
        ]

    def _format_event_line(self, event: Event, score: int) -> str:
        label = self._get_risk_label(score)
        assets_str = self._format_assets(event.affected_assets)
        time_str = event.scheduled_time.strftime("%H:%M")
        end_time = event.scheduled_time + event.impact_window
        time_range = f"{time_str}-{end_time.strftime('%H:%M')}"

        if assets_str and assets_str != "ALL":
            return f"├── {time_range} [{label} - {assets_str}] {event.title}"
        elif assets_str == "ALL":
            return f"├── {time_range} [{label} - ALL] {event.title}"
        else:
            return f"├── {time_range} [{label}] {event.title}"

    def generate_today(
        self,
        current_time: Optional[datetime] = None,
    ) -> str:
        current_time = current_time or datetime.now()
        events = self.risk_aggregator.events
        today_events = self._get_events_for_date(current_time, events)
        today_events.sort(key=lambda e: e.scheduled_time)

        lines: List[str] = []
        date_str = current_time.strftime("%B %d, %Y")
        lines.append(f"TODAY - {date_str}")

        if not today_events:
            lines.append("└── No events scheduled")
        else:
            for i, event in enumerate(today_events):
                score = self._calculate_event_score(event, current_time)
                line = self._format_event_line(event, score)
                if i == len(today_events) - 1:
                    line = line.replace("├──", "└──")
                lines.append(line)

        return "\n".join(lines)

    def generate_week(
        self,
        current_time: Optional[datetime] = None,
    ) -> str:
        current_time = current_time or datetime.now()
        events = self.risk_aggregator.events

        lines: List[str] = []
        high_risk_windows = 0
        blackout_windows: List[str] = []
        elevated_assets: Dict[str, List[str]] = {}

        for day_offset in range(7):
            date = current_time + timedelta(days=day_offset)
            day_events = self._get_events_for_date(date, events)
            day_events.sort(key=lambda e: e.scheduled_time)

            if day_offset == 0:
                day_label = "TODAY"
            elif day_offset == 1:
                day_label = "TOMORROW"
            else:
                day_label = date.strftime("%A").upper()

            date_str = date.strftime("%B %d")
            lines.append(f"{day_label} - {date_str}")

            if not day_events:
                lines.append("└── No events scheduled")
            else:
                for i, event in enumerate(day_events):
                    score = self._calculate_event_score(event, date)
                    line = self._format_event_line(event, score)
                    if i == len(day_events) - 1:
                        line = line.replace("├──", "└──")
                    lines.append(line)

                    if score >= 6:
                        high_risk_windows += 1
                    if score >= 8:
                        time_range = f"{event.scheduled_time.strftime('%a %H:%M')}-{(event.scheduled_time + event.impact_window).strftime('%H:%M')}"
                        blackout_windows.append(time_range)

                    if score >= 6:
                        for asset in event.affected_assets:
                            if asset not in elevated_assets:
                                elevated_assets[asset] = []
                            if event.title not in elevated_assets[asset]:
                                elevated_assets[asset].append(event.title)

            lines.append("")

        lines.append("THIS WEEK SUMMARY:")
        lines.append(f"- High-risk windows: {high_risk_windows}")

        if blackout_windows:
            lines.append(f"- Recommended trading blackouts: {', '.join(blackout_windows[:3])}")
        else:
            lines.append("- Recommended trading blackouts: None")

        if elevated_assets:
            asset_summaries = []
            for asset, reasons in elevated_assets.items():
                reasons_str = " + ".join(reasons[:2])
                asset_summaries.append(f"{asset} ({reasons_str})")
            lines.append(f"- Assets with elevated week risk: {', '.join(asset_summaries)}")
        else:
            lines.append("- Assets with elevated week risk: None")

        return "\n".join(lines)

    def _calculate_event_score(
        self,
        event: Event,
        reference_time: datetime,
    ) -> int:
        max_score = 0
        for asset in event.affected_assets:
            score = self.risk_aggregator.impact_scorer.calculate_score(
                event, asset, reference_time
            )
            max_score = max(max_score, score)
        return max_score
