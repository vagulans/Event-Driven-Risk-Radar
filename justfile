# EDRR - Event-Driven Risk Radar

# Default recipe: show help
default:
    @just --list

# One-time risk check for all assets
check:
    .venv/bin/python -m edrr.main --mode check

# Check risk for a specific asset (e.g., just check-asset BTC)
check-asset asset:
    .venv/bin/python -m edrr.main --mode check --asset {{asset}}

# Run in daemon mode (continuous monitoring)
daemon:
    .venv/bin/python -m edrr.main --mode daemon

# Run daemon with specific asset filter
daemon-asset asset:
    .venv/bin/python -m edrr.main --mode daemon --asset {{asset}}

# Install dependencies
install:
    python3 -m venv .venv
    .venv/bin/pip install -r edrr/requirements.txt

# Run tests
test:
    .venv/bin/python -m pytest tests/ -v

# Run type checking
typecheck:
    .venv/bin/python -m mypy edrr/ --ignore-missing-imports

# Show today's calendar only
today:
    .venv/bin/python -c "import asyncio; from dotenv import load_dotenv; load_dotenv(); from edrr.engine import RiskRadarEngine; e = RiskRadarEngine(); asyncio.run(e._fetch_all_events()); print(e.get_calendar_today())"

# Show week ahead calendar
week:
    .venv/bin/python -c "import asyncio; from dotenv import load_dotenv; load_dotenv(); from edrr.engine import RiskRadarEngine; e = RiskRadarEngine(); asyncio.run(e._fetch_all_events()); print(e.get_calendar_week())"
