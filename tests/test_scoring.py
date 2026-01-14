import pytest
from datetime import datetime, timedelta

from edrr.models.events import Event, EventCategory, EventTier
from edrr.models.config import Config, TIME_MULTIPLIERS, ASSET_EVENT_CORRELATIONS
from edrr.analysis.impact_scorer import ImpactScorer


class TestTimeMultiplierCalculations:
    def setup_method(self):
        self.scorer = ImpactScorer()
        self.base_time = datetime(2025, 1, 15, 12, 0, 0)

    def _create_event(self, scheduled_time: datetime) -> Event:
        return Event(
            id="test-001",
            title="FOMC Meeting",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=scheduled_time,
            impact_window=timedelta(hours=4),
            affected_assets=["SPY", "QQQ", "BTC", "GOLD"],
        )

    def test_under_1h_multiplier(self):
        event = self._create_event(self.base_time + timedelta(minutes=30))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 2.0

    def test_1_to_4h_multiplier(self):
        event = self._create_event(self.base_time + timedelta(hours=2))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.8

    def test_4_to_12h_multiplier(self):
        event = self._create_event(self.base_time + timedelta(hours=8))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.5

    def test_12_to_24h_multiplier(self):
        event = self._create_event(self.base_time + timedelta(hours=18))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.2

    def test_24h_plus_multiplier(self):
        event = self._create_event(self.base_time + timedelta(hours=36))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.0

    def test_within_impact_window_after_event(self):
        event = self._create_event(self.base_time - timedelta(hours=2))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 2.0

    def test_outside_impact_window_after_event(self):
        event = self._create_event(self.base_time - timedelta(hours=6))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 0.0

    def test_boundary_exactly_1h(self):
        event = self._create_event(self.base_time + timedelta(hours=1))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.8

    def test_boundary_exactly_4h(self):
        event = self._create_event(self.base_time + timedelta(hours=4))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.5

    def test_boundary_exactly_12h(self):
        event = self._create_event(self.base_time + timedelta(hours=12))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.2

    def test_boundary_exactly_24h(self):
        event = self._create_event(self.base_time + timedelta(hours=24))
        multiplier = self.scorer._get_time_multiplier(event, self.base_time)
        assert multiplier == 1.0


class TestAssetEventCorrelationWeighting:
    def setup_method(self):
        self.scorer = ImpactScorer()

    def test_spy_economic_correlation(self):
        weight = self.scorer._get_correlation_weight(EventCategory.ECONOMIC, "SPY")
        assert weight == 1.0

    def test_qqq_earnings_correlation(self):
        weight = self.scorer._get_correlation_weight(EventCategory.EARNINGS, "QQQ")
        assert weight == 1.0

    def test_btc_crypto_correlation(self):
        weight = self.scorer._get_correlation_weight(EventCategory.CRYPTO, "BTC")
        assert weight == 1.0

    def test_gold_geopolitical_correlation(self):
        weight = self.scorer._get_correlation_weight(EventCategory.GEOPOLITICAL, "GOLD")
        assert weight == 1.0

    def test_low_correlation_spy_crypto(self):
        weight = self.scorer._get_correlation_weight(EventCategory.CRYPTO, "SPY")
        assert weight == 0.2

    def test_low_correlation_gold_crypto(self):
        weight = self.scorer._get_correlation_weight(EventCategory.CRYPTO, "GOLD")
        assert weight == 0.1

    def test_low_correlation_gold_earnings(self):
        weight = self.scorer._get_correlation_weight(EventCategory.EARNINGS, "GOLD")
        assert weight == 0.1

    def test_unknown_asset_default_weight(self):
        weight = self.scorer._get_correlation_weight(EventCategory.ECONOMIC, "UNKNOWN")
        assert weight == 0.5

    def test_all_assets_all_categories(self):
        assets = ["SPY", "QQQ", "BTC", "GOLD"]
        for asset in assets:
            for category in EventCategory:
                weight = self.scorer._get_correlation_weight(category, asset)
                assert 0.0 <= weight <= 1.0


class TestScoreBounds:
    def setup_method(self):
        self.scorer = ImpactScorer()
        self.base_time = datetime(2025, 1, 15, 12, 0, 0)

    def test_clamp_score_minimum(self):
        assert self.scorer._clamp_score(0.0) == 1
        assert self.scorer._clamp_score(-5.0) == 1
        assert self.scorer._clamp_score(0.5) == 1

    def test_clamp_score_maximum(self):
        assert self.scorer._clamp_score(10.0) == 10
        assert self.scorer._clamp_score(15.0) == 10
        assert self.scorer._clamp_score(100.0) == 10

    def test_clamp_score_rounding(self):
        assert self.scorer._clamp_score(4.4) == 4
        assert self.scorer._clamp_score(4.5) == 4
        assert self.scorer._clamp_score(4.6) == 5
        assert self.scorer._clamp_score(7.2) == 7
        assert self.scorer._clamp_score(7.8) == 8

    def test_calculate_score_returns_int(self):
        event = Event(
            id="test-001",
            title="CPI Release",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=self.base_time + timedelta(hours=2),
            impact_window=timedelta(hours=4),
            affected_assets=["SPY"],
        )
        score = self.scorer.calculate_score(event, "SPY", self.base_time)
        assert isinstance(score, int)

    def test_calculate_score_within_bounds(self):
        for tier in EventTier:
            for category in EventCategory:
                for hours_ahead in [0.5, 2, 8, 18, 36]:
                    event = Event(
                        id=f"test-{tier.value}-{category.value}",
                        title=f"Test Event",
                        category=category,
                        tier=tier,
                        scheduled_time=self.base_time + timedelta(hours=hours_ahead),
                        impact_window=timedelta(hours=4),
                        affected_assets=["SPY", "QQQ", "BTC", "GOLD"],
                    )
                    for asset in ["SPY", "QQQ", "BTC", "GOLD"]:
                        score = self.scorer.calculate_score(event, asset, self.base_time)
                        assert 1 <= score <= 10, f"Score {score} out of bounds for {tier}, {category}, {asset}, {hours_ahead}h"

    def test_high_impact_event_max_score(self):
        event = Event(
            id="test-max",
            title="FOMC Decision",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=self.base_time + timedelta(minutes=30),
            impact_window=timedelta(hours=4),
            affected_assets=["SPY"],
        )
        score = self.scorer.calculate_score(event, "SPY", self.base_time)
        assert score == 10

    def test_low_impact_event_low_score(self):
        event = Event(
            id="test-low",
            title="Minor Crypto Event",
            category=EventCategory.CRYPTO,
            tier=EventTier.TIER_4,
            scheduled_time=self.base_time + timedelta(hours=36),
            impact_window=timedelta(hours=2),
            affected_assets=["GOLD"],
        )
        score = self.scorer.calculate_score(event, "GOLD", self.base_time)
        assert score <= 3


class TestBaseImpact:
    def setup_method(self):
        self.scorer = ImpactScorer()

    def test_tier_1_base_impact(self):
        event = Event(
            id="t1",
            title="Tier 1",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=datetime.now(),
            impact_window=timedelta(hours=4),
        )
        assert self.scorer._get_base_impact(event) == 8.0

    def test_tier_2_base_impact(self):
        event = Event(
            id="t2",
            title="Tier 2",
            category=EventCategory.FED_SPEAKER,
            tier=EventTier.TIER_2,
            scheduled_time=datetime.now(),
            impact_window=timedelta(hours=2),
        )
        assert self.scorer._get_base_impact(event) == 5.0

    def test_tier_3_base_impact(self):
        event = Event(
            id="t3",
            title="Tier 3",
            category=EventCategory.GEOPOLITICAL,
            tier=EventTier.TIER_3,
            scheduled_time=datetime.now(),
            impact_window=timedelta(hours=6),
        )
        assert self.scorer._get_base_impact(event) == 6.0

    def test_tier_4_base_impact(self):
        event = Event(
            id="t4",
            title="Tier 4",
            category=EventCategory.CRYPTO,
            tier=EventTier.TIER_4,
            scheduled_time=datetime.now(),
            impact_window=timedelta(hours=2),
        )
        assert self.scorer._get_base_impact(event) == 4.0


class TestScoreCalculation:
    def setup_method(self):
        self.scorer = ImpactScorer()
        self.base_time = datetime(2025, 1, 15, 12, 0, 0)

    def test_score_formula(self):
        event = Event(
            id="test-formula",
            title="Test",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=self.base_time + timedelta(hours=2),
            impact_window=timedelta(hours=4),
            affected_assets=["SPY"],
        )
        base_impact = 8.0
        time_mult = 1.8
        correlation = 1.0
        expected_raw = base_impact * time_mult * correlation
        expected_score = min(10, max(1, round(expected_raw)))
        
        score = self.scorer.calculate_score(event, "SPY", self.base_time)
        assert score == expected_score

    def test_custom_config_affects_score(self):
        custom_config = Config()
        custom_config.time_multipliers["under_1h"] = 3.0
        custom_scorer = ImpactScorer(config=custom_config)
        
        event = Event(
            id="test-custom",
            title="Test",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_2,
            scheduled_time=self.base_time + timedelta(minutes=30),
            impact_window=timedelta(hours=2),
            affected_assets=["SPY"],
        )
        
        default_score = self.scorer.calculate_score(event, "SPY", self.base_time)
        custom_score = custom_scorer.calculate_score(event, "SPY", self.base_time)
        
        assert custom_score >= default_score

    def test_default_current_time(self):
        event = Event(
            id="test-default-time",
            title="Test",
            category=EventCategory.ECONOMIC,
            tier=EventTier.TIER_1,
            scheduled_time=datetime.now() + timedelta(hours=2),
            impact_window=timedelta(hours=4),
            affected_assets=["SPY"],
        )
        score = self.scorer.calculate_score(event, "SPY")
        assert isinstance(score, int)
        assert 1 <= score <= 10
