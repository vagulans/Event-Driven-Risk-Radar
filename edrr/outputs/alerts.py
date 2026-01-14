from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from edrr.models.config import Config
from edrr.models.events import AssetRisk, Event, RiskWindow
from edrr.analysis.risk_aggregator import ClusterInfo, RiskAggregator


class AlertType(Enum):
    THRESHOLD_CROSSING = "threshold_crossing"
    DANGER_ZONE_ENTRY = "danger_zone_entry"
    NEW_HIGH_IMPACT_EVENT = "new_high_impact_event"
    CLUSTERING_DETECTED = "clustering_detected"


@dataclass
class Alert:
    alert_type: AlertType
    title: str
    message: str
    severity: int
    timestamp: datetime
    assets: List[str]
    event: Optional[Event] = None


class AlertManager:
    def __init__(
        self,
        risk_aggregator: Optional[RiskAggregator] = None,
        config: Optional[Config] = None,
    ) -> None:
        self.config = config or Config()
        self.risk_aggregator = risk_aggregator or RiskAggregator(self.config)
        self._previous_risks: Dict[str, AssetRisk] = {}
        self._known_events: set = set()
        self._alerted_clusters: set = set()

    def check_thresholds(
        self,
        current_time: Optional[datetime] = None,
    ) -> List[Alert]:
        current_time = current_time or datetime.now()
        alerts: List[Alert] = []

        current_risks = self.risk_aggregator.get_current_risk(current_time)
        alerts.extend(self._check_threshold_crossings(current_risks, current_time))

        danger_zones = self.risk_aggregator.get_danger_zones(current_time)
        alerts.extend(self._check_danger_zone_entry(danger_zones, current_time))

        alerts.extend(self._check_new_high_impact_events(current_time))

        clusters = self.risk_aggregator.detect_clustering(current_time)
        alerts.extend(self._check_clustering(clusters, current_time))

        self._previous_risks = current_risks

        return alerts

    def _check_threshold_crossings(
        self,
        current_risks: Dict[str, AssetRisk],
        current_time: datetime,
    ) -> List[Alert]:
        alerts: List[Alert] = []
        thresholds = self.config.risk_thresholds

        for asset, risk in current_risks.items():
            previous = self._previous_risks.get(asset)
            if previous is None:
                continue

            crossings = [
                (thresholds.elevated, "ELEVATED", "Elevated risk detected"),
                (thresholds.high, "HIGH", "High risk detected"),
                (thresholds.danger, "DANGER", "Danger zone entered"),
            ]

            for threshold, level_name, desc in crossings:
                if previous.score < threshold <= risk.score:
                    alerts.append(
                        Alert(
                            alert_type=AlertType.THRESHOLD_CROSSING,
                            title=f"{asset} Risk {level_name}",
                            message=f"{desc} for {asset}. Score: {previous.score} -> {risk.score}",
                            severity=risk.score,
                            timestamp=current_time,
                            assets=[asset],
                            event=risk.next_event,
                        )
                    )

        return alerts

    def _check_danger_zone_entry(
        self,
        danger_zones: Dict[str, List[RiskWindow]],
        current_time: datetime,
    ) -> List[Alert]:
        alerts: List[Alert] = []

        for window in danger_zones.get("intraday", []):
            if window.start_time <= current_time <= window.end_time:
                if window.level >= self.config.risk_thresholds.danger:
                    event = window.events[0] if window.events else None
                    alerts.append(
                        Alert(
                            alert_type=AlertType.DANGER_ZONE_ENTRY,
                            title="DANGER ZONE ACTIVE",
                            message=f"Currently in danger zone. Level: {window.level}. Ends: {window.end_time.strftime('%H:%M')}",
                            severity=window.level,
                            timestamp=current_time,
                            assets=window.assets,
                            event=event,
                        )
                    )

        return alerts

    def _check_new_high_impact_events(
        self,
        current_time: datetime,
    ) -> List[Alert]:
        alerts: List[Alert] = []

        for event in self.risk_aggregator.events:
            if event.id in self._known_events:
                continue

            if event.tier.value == 1:
                alerts.append(
                    Alert(
                        alert_type=AlertType.NEW_HIGH_IMPACT_EVENT,
                        title=f"New Tier 1 Event: {event.title}",
                        message=f"High-impact event scheduled at {event.scheduled_time.strftime('%Y-%m-%d %H:%M')}",
                        severity=8,
                        timestamp=current_time,
                        assets=event.affected_assets,
                        event=event,
                    )
                )

            self._known_events.add(event.id)

        return alerts

    def _check_clustering(
        self,
        clusters: List[ClusterInfo],
        current_time: datetime,
    ) -> List[Alert]:
        alerts: List[Alert] = []

        for cluster in clusters:
            cluster_key = (
                cluster.window_start.isoformat(),
                tuple(e.id for e in cluster.events),
            )
            if cluster_key in self._alerted_clusters:
                continue

            event_titles = ", ".join(e.title for e in cluster.events[:3])
            if len(cluster.events) > 3:
                event_titles += f" (+{len(cluster.events) - 3} more)"

            alerts.append(
                Alert(
                    alert_type=AlertType.CLUSTERING_DETECTED,
                    title=f"Event Cluster Detected ({len(cluster.events)} events)",
                    message=f"Multiple events between {cluster.window_start.strftime('%H:%M')} - {cluster.window_end.strftime('%H:%M')}: {event_titles}. Compound risk: {cluster.compound_risk}",
                    severity=cluster.compound_risk,
                    timestamp=current_time,
                    assets=cluster.assets_affected,
                    event=cluster.events[0] if cluster.events else None,
                )
            )
            self._alerted_clusters.add(cluster_key)

        return alerts

    def send_alert(self, alert: Alert) -> None:
        severity_label = self._get_severity_label(alert.severity)
        print(f"\n{'='*60}")
        print(f"[{severity_label}] {alert.alert_type.value.upper()}")
        print(f"{'='*60}")
        print(f"Title: {alert.title}")
        print(f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Severity: {alert.severity}/10")
        print(f"Assets: {', '.join(alert.assets)}")
        print(f"Message: {alert.message}")
        if alert.event:
            print(f"Related Event: {alert.event.title} at {alert.event.scheduled_time}")
        print(f"{'='*60}\n")

    def _get_severity_label(self, severity: int) -> str:
        if severity >= 9:
            return "CRITICAL"
        elif severity >= 7:
            return "HIGH"
        elif severity >= 5:
            return "ELEVATED"
        else:
            return "INFO"
