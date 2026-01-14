from datetime import datetime, timedelta
from typing import Dict, Optional

from edrr.models.config import Config, TIME_MULTIPLIERS, ASSET_EVENT_CORRELATIONS
from edrr.models.events import Event, EventCategory


class ImpactScorer:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config()
        self.time_multipliers = self.config.time_multipliers
        self.asset_correlations = self.config.asset_correlations

    def calculate_score(
        self,
        event: Event,
        asset: str,
        current_time: Optional[datetime] = None,
    ) -> int:
        current_time = current_time or datetime.now()
        
        base_impact = self._get_base_impact(event)
        time_multiplier = self._get_time_multiplier(event, current_time)
        correlation_weight = self._get_correlation_weight(event.category, asset)
        
        raw_score = base_impact * time_multiplier * correlation_weight
        return self._clamp_score(raw_score)

    def _get_base_impact(self, event: Event) -> float:
        tier_impacts: Dict[int, float] = {
            1: 8.0,
            2: 5.0,
            3: 6.0,
            4: 4.0,
        }
        return tier_impacts.get(event.tier.value, 5.0)

    def _get_time_multiplier(self, event: Event, current_time: datetime) -> float:
        time_until_event = event.scheduled_time - current_time
        hours_until = time_until_event.total_seconds() / 3600

        if hours_until < 0:
            hours_since = abs(hours_until)
            impact_hours = event.impact_window.total_seconds() / 3600
            if hours_since <= impact_hours:
                return self.time_multipliers.get("under_1h", 2.0)
            return 0.0

        if hours_until < 1:
            return self.time_multipliers.get("under_1h", 2.0)
        elif hours_until < 4:
            return self.time_multipliers.get("1_to_4h", 1.8)
        elif hours_until < 12:
            return self.time_multipliers.get("4_to_12h", 1.5)
        elif hours_until < 24:
            return self.time_multipliers.get("12_to_24h", 1.2)
        else:
            return self.time_multipliers.get("24h_plus", 1.0)

    def _get_correlation_weight(self, category: EventCategory, asset: str) -> float:
        asset_correlations = self.asset_correlations.get(asset, {})
        return asset_correlations.get(category.value, 0.5)

    def _clamp_score(self, raw_score: float) -> int:
        clamped = max(1, min(10, round(raw_score)))
        return clamped
