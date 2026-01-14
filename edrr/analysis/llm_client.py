import asyncio
import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from edrr.models.events import Event, EventCategory, EventTier


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.client: Optional[AsyncOpenAI] = None
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1.0

    async def analyze_event(self, event: Event) -> Dict[str, Any]:
        prompt = f"""Analyze the following market event and assess its potential impact:

Event: {event.title}
Category: {event.category.value}
Tier: {event.tier.value}
Scheduled Time: {event.scheduled_time.isoformat()}
Impact Window: {event.impact_window}
Affected Assets: {', '.join(event.affected_assets)}

Provide a JSON response with:
1. "impact_score": integer 1-10 (10 being highest impact)
2. "volatility_expectation": "low", "medium", "high", or "extreme"
3. "direction_bias": "bullish", "bearish", or "neutral"
4. "key_risks": list of key risk factors
5. "trading_implications": brief trading guidance

Respond with valid JSON only."""

        response = await self._call_with_retry(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "impact_score": event.tier.value * 2,
                "volatility_expectation": "medium",
                "direction_bias": "neutral",
                "key_risks": ["Unable to parse LLM response"],
                "trading_implications": "Exercise caution",
            }

    async def classify_news(self, headline: str, content: str) -> Dict[str, Any]:
        prompt = f"""Analyze this news article for market-moving potential:

Headline: {headline}
Content: {content[:1000]}

Classify and respond with valid JSON:
1. "is_market_moving": boolean - true if this could significantly move markets
2. "category": one of ["economic", "fed_speaker", "earnings", "geopolitical", "crypto", "regulatory"]
3. "tier": integer 1-4 (1=highest impact, 4=lowest)
4. "affected_assets": list of affected assets from ["SPY", "QQQ", "BTC", "GOLD", "ETH"]
5. "impact_hours": estimated hours of market impact (1-48)
6. "confidence": float 0-1 indicating classification confidence

Respond with valid JSON only."""

        response = await self._call_with_retry(prompt)
        try:
            result = json.loads(response)
            if "category" in result:
                result["category"] = EventCategory(result["category"])
            if "tier" in result:
                result["tier"] = EventTier(result["tier"])
            return result
        except (json.JSONDecodeError, ValueError):
            return {
                "is_market_moving": False,
                "category": EventCategory.GEOPOLITICAL,
                "tier": EventTier.TIER_3,
                "affected_assets": [],
                "impact_hours": 6,
                "confidence": 0.0,
            }

    async def _call_with_retry(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("LLM client not configured - OPENAI_API_KEY not set")
        
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a financial market analyst. Respond only with valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
        raise last_error or Exception("Max retries exceeded")
