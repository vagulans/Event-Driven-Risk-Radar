import os
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class RiskThresholds:
    low: int = 3
    elevated: int = 5
    high: int = 7
    danger: int = 9


TIME_MULTIPLIERS: Dict[str, float] = {
    "24h_plus": 1.0,
    "12_to_24h": 1.2,
    "4_to_12h": 1.5,
    "1_to_4h": 1.8,
    "under_1h": 2.0,
}


ASSET_EVENT_CORRELATIONS: Dict[str, Dict[str, float]] = {
    "SPY": {
        "economic": 1.0,
        "fed_speaker": 0.9,
        "earnings": 0.8,
        "geopolitical": 0.7,
        "crypto": 0.2,
        "regulatory": 0.5,
    },
    "QQQ": {
        "economic": 0.9,
        "fed_speaker": 0.85,
        "earnings": 1.0,
        "geopolitical": 0.6,
        "crypto": 0.3,
        "regulatory": 0.5,
    },
    "BTC": {
        "economic": 0.6,
        "fed_speaker": 0.5,
        "earnings": 0.2,
        "geopolitical": 0.8,
        "crypto": 1.0,
        "regulatory": 0.9,
    },
    "GOLD": {
        "economic": 0.9,
        "fed_speaker": 0.8,
        "earnings": 0.1,
        "geopolitical": 1.0,
        "crypto": 0.1,
        "regulatory": 0.3,
    },
}


@dataclass
class Config:
    calendar_poll_interval_seconds: int = 3600
    news_poll_interval_seconds: int = 300
    risk_recalc_interval_seconds: int = 60
    event_proximity_threshold_hours: int = 2
    
    risk_thresholds: RiskThresholds = field(default_factory=RiskThresholds)
    time_multipliers: Dict[str, float] = field(default_factory=lambda: TIME_MULTIPLIERS.copy())
    asset_correlations: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: {k: v.copy() for k, v in ASSET_EVENT_CORRELATIONS.items()}
    )
    
    openai_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    news_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("NEWS_API_KEY"))
    redis_url: Optional[str] = field(default_factory=lambda: os.environ.get("REDIS_URL"))
