from dataclasses import dataclass
from typing import Optional

from edrr.models.events import AssetRisk, Event
from edrr.models.config import Config


@dataclass
class Recommendation:
    asset: str
    risk_level: int
    action: str
    guidance: str
    next_event: Optional[Event] = None


class RecommendationEngine:
    RECOMMENDATIONS = {
        (1, 3): ("TRADE NORMALLY", "Risk is low. Normal trading conditions apply."),
        (4, 5): ("AWARENESS", "Elevated awareness recommended. Monitor upcoming events."),
        (6, 7): ("REDUCE EXPOSURE", "Consider reducing position sizes. Tighten stops."),
        (8, 9): ("CLOSE/HEDGE", "Close speculative positions or hedge existing exposure."),
        (10, 10): ("DO NOT TRADE", "Extreme risk window. Avoid new positions entirely."),
    }

    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config()

    def get_recommendation(self, asset_risk: AssetRisk) -> Recommendation:
        action, guidance = self._get_action_and_guidance(asset_risk.score)
        return Recommendation(
            asset=asset_risk.asset,
            risk_level=asset_risk.score,
            action=action,
            guidance=guidance,
            next_event=asset_risk.next_event,
        )

    def _get_action_and_guidance(self, score: int) -> tuple[str, str]:
        for (low, high), (action, guidance) in self.RECOMMENDATIONS.items():
            if low <= score <= high:
                return action, guidance
        return "UNKNOWN", "Unable to determine recommendation."

    def get_all_recommendations(
        self, asset_risks: dict[str, AssetRisk]
    ) -> dict[str, Recommendation]:
        return {
            asset: self.get_recommendation(risk)
            for asset, risk in asset_risks.items()
        }

    def format_recommendation(self, recommendation: Recommendation) -> str:
        lines = [
            f"[{recommendation.asset}] Risk Level: {recommendation.risk_level}/10",
            f"  Action: {recommendation.action}",
            f"  Guidance: {recommendation.guidance}",
        ]
        if recommendation.next_event:
            lines.append(
                f"  Next Event: {recommendation.next_event.title} "
                f"at {recommendation.next_event.scheduled_time.strftime('%Y-%m-%d %H:%M')}"
            )
        return "\n".join(lines)
