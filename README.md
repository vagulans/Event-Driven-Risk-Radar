# Event-Driven Risk Radar (EDRR)

A forward-looking early warning system that identifies high-risk trading windows before they happen for equities, Bitcoin, and gold.

## Features

- **Multi-Source Event Aggregation**: Pulls from economic calendars, Fed speaker schedules, mega-cap earnings, news feeds, and crypto events
- **Intelligent Risk Scoring**: 1-10 risk scale with time-based multipliers and asset-event correlation weights
- **Cluster Detection**: Identifies compound risk when multiple events occur in tight windows
- **Actionable Recommendations**: Maps risk levels to trading guidance (trade normally → do not trade)
- **Real-Time Monitoring**: Continuous polling with configurable intervals

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# One-time risk check
python3 -m edrr.main --mode check

# Filter by asset
python3 -m edrr.main --mode check --asset BTC

# Continuous monitoring (daemon mode)
python3 -m edrr.main --mode daemon
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for LLM-powered event analysis |
| `NEWS_API_KEY` | NewsAPI key for emerging event detection |
| `REDIS_URL` | Optional Redis URL for caching |

## Project Structure

```
edrr/
├── models/
│   ├── events.py      # Event, RiskWindow, AssetRisk dataclasses
│   └── config.py      # Config, thresholds, time multipliers
├── sources/
│   ├── base.py              # Abstract EventSource class
│   ├── economic_calendar.py # FOMC, CPI, NFP, GDP events
│   ├── fed_calendar.py      # Fed speaker schedules
│   ├── earnings_calendar.py # Mega-cap earnings (AAPL, NVDA, etc.)
│   ├── news_monitor.py      # Emerging events from news feeds
│   └── crypto_events.py     # Protocol upgrades, token unlocks, SEC
├── analysis/
│   ├── llm_client.py      # OpenAI-powered event analysis
│   ├── impact_scorer.py   # Risk score calculation
│   └── risk_aggregator.py # Per-asset risk aggregation
├── outputs/
│   ├── calendar_view.py     # Daily/weekly calendar generation
│   ├── alerts.py            # Threshold-based alerting
│   └── recommendations.py   # Trading action guidance
├── api/
│   └── endpoints.py   # REST API for trading system integration
├── scheduler.py       # APScheduler-based job scheduling
├── engine.py          # Main orchestration engine
└── main.py           # CLI entry point
```

## Risk Levels

| Score | Status | Recommendation |
|-------|--------|----------------|
| 1-3 | LOW | Trade normally |
| 4-5 | MODERATE | Heightened awareness |
| 6-7 | ELEVATED | Reduce exposure |
| 8-9 | HIGH | Close positions / hedge |
| 10 | CRITICAL | Do not trade |

## Event Tiers

- **Tier 1**: Major scheduled events (FOMC, CPI, mega-cap earnings)
- **Tier 2**: Fed speakers, secondary data releases
- **Tier 3**: Emerging/breaking events (geopolitical, regulatory)
- **Tier 4**: Crypto-specific (protocol upgrades, token unlocks)

## Time Multipliers

Events closer in time carry higher risk multipliers:

| Time to Event | Multiplier |
|---------------|------------|
| >24 hours | 1.0x |
| 12-24 hours | 1.2x |
| 4-12 hours | 1.5x |
| 1-4 hours | 1.8x |
| <1 hour | 2.0x |

## API Endpoints

When running in daemon mode, the following endpoints are available:

| Endpoint | Description |
|----------|-------------|
| `GET /risk` | Current risk for all assets |
| `GET /risk/{asset}` | Current risk for specific asset |
| `GET /calendar/today` | Today's event calendar |
| `GET /calendar/week` | Week-ahead calendar |
| `GET /recommendation/{asset}` | Trading recommendation |
| `GET /health` | Health check |

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Type Checking

```bash
python3 -m mypy edrr/ --ignore-missing-imports
```

## License

MIT
