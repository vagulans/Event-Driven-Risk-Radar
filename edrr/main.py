"""Event-Driven Risk Radar (EDRR) - Main Entry Point"""

import argparse
import asyncio
import signal
import sys
from typing import Optional

from edrr.engine import RiskRadarEngine
from edrr.models.config import Config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="edrr",
        description="Event-Driven Risk Radar - Forward-looking early warning system for trading",
    )
    parser.add_argument(
        "--mode",
        choices=["daemon", "check"],
        default="check",
        help="Run mode: 'daemon' for continuous monitoring, 'check' for one-time status (default: check)",
    )
    parser.add_argument(
        "--asset",
        type=str,
        default=None,
        help="Filter by asset (e.g., SPY, QQQ, BTC, GOLD)",
    )
    return parser.parse_args()


async def run_check(engine: RiskRadarEngine, asset: Optional[str] = None) -> None:
    await engine._fetch_all_events()
    
    print("\n" + "=" * 60)
    print("EVENT-DRIVEN RISK RADAR - STATUS CHECK")
    print("=" * 60)
    
    print("\n" + engine.get_calendar_today())
    print("\n" + "-" * 60)
    print("WEEK AHEAD")
    print("-" * 60)
    print(engine.get_calendar_week())
    
    print("\n" + "-" * 60)
    print("CURRENT RISK STATUS")
    print("-" * 60)
    
    status = engine.get_status()
    
    if asset:
        asset_upper = asset.upper()
        if asset_upper in status:
            risk = status[asset_upper]
            _print_asset_risk(asset_upper, risk)
        else:
            print(f"Asset '{asset_upper}' not found. Available: {', '.join(status.keys())}")
    else:
        for asset_name, risk in sorted(status.items()):
            _print_asset_risk(asset_name, risk)
    
    print("\n" + "-" * 60)
    print("RECOMMENDATIONS")
    print("-" * 60)
    
    for asset_name, risk in sorted(status.items()):
        if asset and asset.upper() != asset_name:
            continue
        rec = engine.recommendation_engine.get_recommendation(risk)
        formatted = engine.recommendation_engine.format_recommendation(rec)
        print(formatted)


def _print_asset_risk(asset_name: str, risk) -> None:
    status_str = risk.status.upper() if risk.status else "UNKNOWN"
    score = risk.score
    next_event_str = ""
    if risk.next_event:
        next_event_str = f" | Next: {risk.next_event.title} @ {risk.next_event.scheduled_time.strftime('%H:%M')}"
    print(f"  {asset_name:6} | Score: {score:4.1f} | Status: {status_str:10}{next_event_str}")


async def run_daemon(engine: RiskRadarEngine, asset: Optional[str] = None) -> None:
    print("\n" + "=" * 60)
    print("EVENT-DRIVEN RISK RADAR - DAEMON MODE")
    print("=" * 60)
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop\n")
    
    await run_check(engine, asset)
    
    await engine.start()
    
    stop_event = asyncio.Event()
    
    def signal_handler(sig, frame):
        print("\n\nShutting down...")
        stop_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await stop_event.wait()
    finally:
        engine.stop()
        print("Stopped.")


async def async_main() -> None:
    args = parse_args()
    
    config = Config()
    engine = RiskRadarEngine(config)
    
    if args.mode == "daemon":
        await run_daemon(engine, args.asset)
    else:
        await run_check(engine, args.asset)


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
