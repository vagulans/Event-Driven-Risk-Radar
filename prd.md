# Event-Driven Risk Radar (EDRR)
## Product Requirements Document v2

**Date:** January 13, 2026

---

## What This Is

A forward-looking early warning system that identifies high-risk trading windows before they happen. The system continuously monitors for planned and emerging events that could cause sudden market moves in equities, Bitcoin, and gold—telling you when to stop trading or reduce exposure.

**The Core Problem:** Markets move violently around events. Trump's Detroit speech today moved Bitcoin $2,000 in minutes. Traders get caught in positions during these windows, taking unnecessary losses. With advance warning, you can simply step aside.

**The Solution:** An always-on radar that surfaces dangerous trading windows—hours, days, or specific time blocks where volatility risk is elevated—so you can plan around them.

---

## Core Philosophy

### Events, Not Sentiment
This system tracks **concrete events** with identifiable times and sources—not Twitter mood, not fear/greed indexes, not vague "market sentiment." If it doesn't have a scheduled or emerging time window, it's out of scope.

### Forward-Looking Only
We don't care about what just happened. We care about what's coming in the next hours and days. The system should answer: "What windows should I avoid trading in today? This week?"

### High-Risk Window Identification
The primary output isn't a continuous risk score—it's **identified danger zones**: specific time blocks where trading carries elevated risk. These could be:
- A 2-hour window around an FOMC announcement
- An entire day when Trump has multiple scheduled appearances
- A week containing earnings from 5 mega-cap tech companies plus CPI data

---

## Event Categories

### Tier 1: Known Schedule, High Impact
Events with confirmed times that historically move markets significantly.

| Category | Examples | Typical Impact Window |
|----------|----------|----------------------|
| Central Bank Decisions | FOMC, ECB, BOJ rate decisions | 2-4 hours around announcement |
| Major Economic Data | CPI, NFP, GDP releases | 1-2 hours after release |
| Mega-Cap Earnings | AAPL, MSFT, NVDA, GOOGL, AMZN, TSLA, META | After-hours + next morning |
| Crypto Regulatory | SEC ETF deadlines, major rulings | Full day |

### Tier 2: Known Schedule, Variable Impact
Events that are scheduled but impact varies based on context.

| Category | Examples | Typical Impact Window |
|----------|----------|----------------------|
| Fed Speaker Events | Powell, Waller, other FOMC members | 1-2 hours around speech |
| Presidential Appearances | Speeches, press conferences, rallies | During + 1 hour after |
| Congressional Hearings | Finance, crypto, tech-related | During session |
| Secondary Economic Data | Jobless claims, PMI, retail sales | 30-60 minutes after |
| Sector Earnings | Bank earnings week, retail earnings | Varies by clustering |

### Tier 3: Emerging & Semi-Scheduled
Events that develop or get announced with shorter notice.

| Category | Examples | Detection Method |
|----------|----------|------------------|
| Breaking Geopolitical | Military actions, trade announcements | News monitoring + LLM evaluation |
| Unscheduled Presidential | Surprise announcements, executive orders | White House feed + news monitoring |
| Regulatory Surprises | SEC actions, DOJ announcements | Agency feeds + news monitoring |
| Market Structure Events | Exchange outages, flash crashes | Real-time monitoring |

### Tier 4: Crypto-Specific
Events unique to cryptocurrency markets.

| Category | Examples | Typical Impact Window |
|----------|----------|----------------------|
| Protocol Events | Bitcoin halving, major upgrades | Days around event |
| Token Unlocks | Large scheduled unlocks | Day of unlock |
| Exchange Events | Major listings, delistings, hacks | Immediate + 24 hours |

---

## Asset-Event Correlation

Not all events affect all assets equally. The system maintains correlation weights:

**Bitcoin is highly sensitive to:**
- Trump speeches/announcements (recent pattern: very high)
- SEC/regulatory news (very high)
- FOMC decisions (high)
- Risk-on/risk-off macro shifts (high)

**Equities are highly sensitive to:**
- FOMC decisions (very high)
- CPI/employment data (very high)
- Mega-cap earnings (high for indices)
- Trade policy announcements (high)

**Gold is highly sensitive to:**
- FOMC decisions (very high)
- Inflation data (very high)
- Geopolitical escalation (very high)
- Dollar strength events (high)

---

## LLM Integration Points

### 1. Event Discovery & Classification
Use LLMs to monitor news feeds and identify emerging events that don't appear on standard calendars.

**Input:** Raw news headlines, press releases, social posts from official accounts
**Output:** Structured event with estimated time, category, and affected assets
**Prompt Focus:** "Is this announcing a concrete future event? When? What markets could it affect?"

### 2. Impact Assessment
Use LLMs to evaluate the potential significance of detected events.

**Input:** Event details + current market context + historical patterns
**Output:** Impact score (1-10) with reasoning
**Prompt Focus:** "Given current market conditions, how likely is this event to cause significant volatility? Why?"

### 3. Risk Window Synthesis
Use LLMs to analyze clusters of events and identify compounding risk.

**Input:** List of upcoming events in a time window
**Output:** Narrative risk assessment for the period
**Prompt Focus:** "Multiple events cluster in this window. What's the combined risk profile? Are there interaction effects?"

### 4. Context Enrichment
Use LLMs to add context that affects impact assessment.

**Input:** Event + recent related news + market positioning
**Output:** Contextual factors that raise or lower expected impact
**Prompt Focus:** "What recent developments make this event more or less significant than usual?"

---

## Primary Outputs

### 1. Risk Calendar View
A forward-looking calendar showing danger zones:

```
TODAY - January 13, 2026
├── 09:30-10:30 [MODERATE] Jobless Claims Release
├── 18:00-20:00 [HIGH - BTC] Trump Detroit Speech
└── After Hours [ELEVATED] No major earnings

TOMORROW - January 14
├── All Day [ELEVATED - BTC] SEC ETF Response Deadline
└── 14:00-16:00 [MODERATE] Fed Governor Speech

WEDNESDAY - January 15
└── 14:00-17:00 [CRITICAL - ALL] FOMC Rate Decision

THIS WEEK SUMMARY:
- High-risk windows: 3
- Recommended trading blackouts: Wed 13:00-17:00
- Assets with elevated week risk: BTC (SEC deadline + Trump), All (FOMC)
```

### 2. Real-Time Risk Level
Current aggregate risk for each asset class:

| Asset | Current Level | Status | Next Event |
|-------|---------------|--------|------------|
| Bitcoin | 7.8/10 | HIGH | Trump Speech (6 hrs) |
| Equities | 5.2/10 | MODERATE | FOMC (2 days) |
| Gold | 4.1/10 | LOW | FOMC (2 days) |

### 3. Danger Zone Alerts
Push notifications when entering or approaching high-risk windows:

**ALERT: Bitcoin risk elevated to HIGH (7.8)**
- Trump Detroit speech begins in 6 hours
- Recent pattern: BTC moved $2k+ on last 3 Trump appearances
- Recommendation: Reduce BTC exposure before 5 PM EST

### 4. Trading Recommendations
Clear, actionable guidance:

| Risk Level | Recommendation |
|------------|----------------|
| 1-3 (Low) | Trade normally |
| 4-5 (Moderate) | Trade with awareness, tighter stops |
| 6-7 (Elevated) | Reduce position sizes, avoid entries near event |
| 8-9 (High) | Close or hedge positions, no new entries |
| 10 (Critical) | Do not trade this asset |

---

## High-Risk Period Identification

The system's primary job is identifying these danger zones:

### Intraday Windows
Specific hours to avoid:
- 30 minutes before/after major data releases
- During Fed speeches
- During presidential appearances
- First hour after surprise announcements

### High-Risk Days
Full days with elevated caution:
- FOMC announcement days
- CPI/NFP release days
- Days with 3+ Tier 1/2 events
- Days with critical regulatory deadlines

### High-Risk Weeks
Extended periods requiring adjusted strategy:
- Mega-cap earnings weeks (especially when clustered)
- FOMC meeting weeks
- Weeks with multiple economic releases
- Weeks with known political catalysts

### Event Clustering Detection
The system specifically watches for dangerous combinations:
- Multiple high-impact events within 24 hours
- Earnings + economic data on same day
- Political events + regulatory deadlines overlapping
- Any 3+ medium-impact events in a 6-hour window

---

## Data Sources

### Structured Calendars
- Economic calendars (FOMC, CPI, NFP, GDP schedules)
- Federal Reserve calendar (speaker schedules)
- Earnings calendars (filtered to high-impact names)
- SEC EDGAR (filing deadlines, ETF decisions)
- Crypto event aggregators (unlocks, upgrades)

### Semi-Structured Feeds
- White House public schedule
- Congressional hearing schedules
- Central bank announcement feeds

### Unstructured Monitoring (LLM-Processed)
- News API feeds (Reuters, AP, financial news)
- Official government/agency RSS feeds
- Official social accounts (verified only)

---

## System Behavior

### Continuous Operations
- Poll structured calendars hourly
- Monitor news feeds every 5 minutes
- Recalculate risk scores every minute when events are within 2 hours
- Push alerts immediately when thresholds crossed

### Risk Score Dynamics
Scores intensify as events approach:
- 24+ hours out: Base impact score
- 12-24 hours: 1.2x multiplier
- 4-12 hours: 1.5x multiplier
- 1-4 hours: 1.8x multiplier
- Under 1 hour: 2.0x multiplier

### Alert Logic
- Alert when any asset crosses configured threshold
- Alert when entering a pre-identified danger zone
- Alert when new high-impact event detected
- Alert when event clustering creates compound risk

---

## Integration with Trading Systems

The Risk Radar outputs should feed directly into trading decisions:

**Pre-Trade Check:** Before any trade, query current risk level. If above threshold, block or warn.

**Position Sizing:** Multiply intended position size by risk-adjusted factor (lower size in elevated risk).

**Session Planning:** At start of day/week, review upcoming danger zones and plan trading windows accordingly.

**Emergency Response:** When critical alerts fire, automated systems should halt new entries or reduce exposure.

---

## Success Criteria

1. **Coverage:** Capture 95%+ of events that cause >2% moves in monitored assets
2. **Timeliness:** Surface scheduled events 24+ hours in advance; emerging events within 15 minutes of detection
3. **Accuracy:** <10% false positive rate on high-risk alerts
4. **Actionability:** Clear, specific recommendations that can be acted on immediately

---

## Out of Scope (V1)

- Sentiment analysis or social media mood tracking
- Price prediction or directional forecasting
- Backtesting or historical analysis
- Multi-user support or personalization
- Automated trade execution (advisory only)

---

## Summary

The Event-Driven Risk Radar is a defensive system. It doesn't tell you what to trade—it tells you **when not to trade**. By identifying high-risk windows in advance, you can step aside during dangerous periods and trade with confidence during calmer windows.

The system combines structured calendar data with LLM-powered monitoring to surface both known and emerging risks, delivering clear recommendations: trade, reduce, or stop.