from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class EventCategory(Enum):
    ECONOMIC = "economic"
    FED_SPEAKER = "fed_speaker"
    EARNINGS = "earnings"
    GEOPOLITICAL = "geopolitical"
    CRYPTO = "crypto"
    REGULATORY = "regulatory"


class EventTier(Enum):
    TIER_1 = 1  # High impact: FOMC, CPI, NFP, GDP, mega-cap earnings
    TIER_2 = 2  # Medium impact: Fed speakers, secondary data
    TIER_3 = 3  # Emerging: geopolitical, unscheduled events
    TIER_4 = 4  # Crypto-specific: protocol upgrades, token unlocks


@dataclass
class Event:
    id: str
    title: str
    category: EventCategory
    tier: EventTier
    scheduled_time: datetime
    impact_window: timedelta
    affected_assets: List[str] = field(default_factory=list)


@dataclass
class RiskWindow:
    start_time: datetime
    end_time: datetime
    level: int  # 1-10 scale
    events: List[Event] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)


@dataclass
class AssetRisk:
    asset: str
    score: int  # 1-10 scale
    status: str  # e.g., "normal", "elevated", "danger"
    next_event: Optional[Event] = None
