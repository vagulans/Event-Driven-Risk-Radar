import pytest
from datetime import datetime, timedelta

from edrr.models.events import (
    Event,
    RiskWindow,
    AssetRisk,
    EventCategory,
    EventTier,
)
from edrr.models.config import (
    Config,
    RiskThresholds,
    TIME_MULTIPLIERS,
    ASSET_EVENT_CORRELATIONS,
)


class TestEventCategory:
    def test_enum_values(self):
        assert EventCategory.ECONOMIC.value == "economic"
        assert EventCategory.FED_SPEAKER.value == "fed_speaker"
        assert EventCategory.EARNINGS.value == "earnings"
        assert EventCategory.GEOPOLITICAL.value == "geopolitical"
        assert EventCategory.CRYPTO.value == "crypto"
        assert EventCategory.REGULATORY.value == "regulatory"

    def test_enum_count(self):
        assert len(EventCategory) == 6


class TestEventTier:
    def test_enum_values(self):
        assert EventTier.TIER_1.value == 1
        assert EventTier.TIER_2.value == 2
        assert EventTier.TIER_3.value == 3
        assert EventTier.TIER_4.value == 4

    def test_enum_count(self):
        assert len(EventTier) == 4


class TestEvent:
    def test_event_creation(self):
        now = datetime.now()
        event = Event(
            id="test-001",
            title="FOMC Meeting",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=now,
            impact_window=timedelta(hours=4),
            affected_assets=["SPY", "QQQ", "BTC", "GOLD"],
        )
        assert event.id == "test-001"
        assert event.title == "FOMC Meeting"
        assert event.category == EventCategory.ECONOMIC
        assert event.tier == EventTier.TIER_1
        assert event.scheduled_time == now
        assert event.impact_window == timedelta(hours=4)
        assert event.affected_assets == ["SPY", "QQQ", "BTC", "GOLD"]

    def test_event_default_affected_assets(self):
        now = datetime.now()
        event = Event(
            id="test-002",
            title="Fed Speech",
            category=EventCategory.FED_SPEAKER,
            tier=EventTier.TIER_2,
            scheduled_time=now,
            impact_window=timedelta(hours=2),
        )
        assert event.affected_assets == []

    def test_event_all_categories(self):
        now = datetime.now()
        for category in EventCategory:
            event = Event(
                id=f"test-{category.value}",
                title=f"Test {category.value}",
                category=category,
                tier=EventTier.TIER_1,
                scheduled_time=now,
                impact_window=timedelta(hours=1),
            )
            assert event.category == category


class TestRiskWindow:
    def test_risk_window_creation(self):
        now = datetime.now()
        end = now + timedelta(hours=4)
        event = Event(
            id="test-001",
            title="CPI Release",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=now,
            impact_window=timedelta(hours=4),
            affected_assets=["SPY"],
        )
        window = RiskWindow(
            start_time=now,
            end_time=end,
            level=8,
            events=[event],
            assets=["SPY", "QQQ"],
        )
        assert window.start_time == now
        assert window.end_time == end
        assert window.level == 8
        assert len(window.events) == 1
        assert window.events[0].id == "test-001"
        assert window.assets == ["SPY", "QQQ"]

    def test_risk_window_default_lists(self):
        now = datetime.now()
        window = RiskWindow(
            start_time=now,
            end_time=now + timedelta(hours=1),
            level=5,
        )
        assert window.events == []
        assert window.assets == []

    def test_risk_window_level_range(self):
        now = datetime.now()
        for level in range(1, 11):
            window = RiskWindow(
                start_time=now,
                end_time=now + timedelta(hours=1),
                level=level,
            )
            assert window.level == level


class TestAssetRisk:
    def test_asset_risk_creation(self):
        risk = AssetRisk(
            asset="SPY",
            score=7,
            status="elevated",
        )
        assert risk.asset == "SPY"
        assert risk.score == 7
        assert risk.status == "elevated"
        assert risk.next_event is None

    def test_asset_risk_with_next_event(self):
        now = datetime.now()
        event = Event(
            id="test-001",
            title="NFP Report",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=now,
            impact_window=timedelta(hours=4),
        )
        risk = AssetRisk(
            asset="BTC",
            score=9,
            status="danger",
            next_event=event,
        )
        assert risk.next_event is not None
        assert risk.next_event.id == "test-001"

    def test_asset_risk_all_status_values(self):
        statuses = ["normal", "elevated", "high", "danger"]
        for status in statuses:
            risk = AssetRisk(asset="GOLD", score=5, status=status)
            assert risk.status == status


class TestRiskThresholds:
    def test_default_values(self):
        thresholds = RiskThresholds()
        assert thresholds.low == 3
        assert thresholds.elevated == 5
        assert thresholds.high == 7
        assert thresholds.danger == 9

    def test_custom_values(self):
        thresholds = RiskThresholds(low=2, elevated=4, high=6, danger=8)
        assert thresholds.low == 2
        assert thresholds.elevated == 4
        assert thresholds.high == 6
        assert thresholds.danger == 8


class TestTimeMultipliers:
    def test_time_multipliers_values(self):
        assert TIME_MULTIPLIERS["24h_plus"] == 1.0
        assert TIME_MULTIPLIERS["12_to_24h"] == 1.2
        assert TIME_MULTIPLIERS["4_to_12h"] == 1.5
        assert TIME_MULTIPLIERS["1_to_4h"] == 1.8
        assert TIME_MULTIPLIERS["under_1h"] == 2.0

    def test_time_multipliers_count(self):
        assert len(TIME_MULTIPLIERS) == 5

    def test_time_multipliers_increasing(self):
        ordered = ["24h_plus", "12_to_24h", "4_to_12h", "1_to_4h", "under_1h"]
        for i in range(len(ordered) - 1):
            assert TIME_MULTIPLIERS[ordered[i]] < TIME_MULTIPLIERS[ordered[i + 1]]


class TestAssetEventCorrelations:
    def test_assets_present(self):
        assert "SPY" in ASSET_EVENT_CORRELATIONS
        assert "QQQ" in ASSET_EVENT_CORRELATIONS
        assert "BTC" in ASSET_EVENT_CORRELATIONS
        assert "GOLD" in ASSET_EVENT_CORRELATIONS

    def test_all_categories_in_each_asset(self):
        categories = ["economic", "fed_speaker", "earnings", "geopolitical", "crypto", "regulatory"]
        for asset in ASSET_EVENT_CORRELATIONS:
            for category in categories:
                assert category in ASSET_EVENT_CORRELATIONS[asset]

    def test_correlation_range(self):
        for asset, correlations in ASSET_EVENT_CORRELATIONS.items():
            for category, weight in correlations.items():
                assert 0.0 <= weight <= 1.0, f"{asset} {category} weight {weight} out of range"


class TestConfig:
    def test_default_values(self):
        config = Config()
        assert config.calendar_poll_interval_seconds == 3600
        assert config.news_poll_interval_seconds == 300
        assert config.risk_recalc_interval_seconds == 60
        assert config.event_proximity_threshold_hours == 2

    def test_default_risk_thresholds(self):
        config = Config()
        assert config.risk_thresholds.low == 3
        assert config.risk_thresholds.elevated == 5
        assert config.risk_thresholds.high == 7
        assert config.risk_thresholds.danger == 9

    def test_default_time_multipliers(self):
        config = Config()
        assert config.time_multipliers == TIME_MULTIPLIERS

    def test_default_asset_correlations(self):
        config = Config()
        assert "SPY" in config.asset_correlations
        assert "QQQ" in config.asset_correlations
        assert "BTC" in config.asset_correlations
        assert "GOLD" in config.asset_correlations

    def test_config_independence(self):
        config1 = Config()
        config2 = Config()
        config1.time_multipliers["under_1h"] = 3.0
        assert config2.time_multipliers["under_1h"] == 2.0
