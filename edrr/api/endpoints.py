from datetime import datetime
from typing import Any, Dict, Optional

from aiohttp import web

from edrr.models.config import Config
from edrr.models.events import AssetRisk
from edrr.analysis.risk_aggregator import RiskAggregator
from edrr.outputs.calendar_view import CalendarView
from edrr.outputs.recommendations import RecommendationEngine


class EDRRApi:
    def __init__(
        self,
        risk_aggregator: Optional[RiskAggregator] = None,
        config: Optional[Config] = None,
    ) -> None:
        self.config = config or Config()
        self.risk_aggregator = risk_aggregator or RiskAggregator(self.config)
        self.calendar_view = CalendarView(self.risk_aggregator, self.config)
        self.recommendation_engine = RecommendationEngine(self.config)

    def create_app(self) -> web.Application:
        app = web.Application()
        app.router.add_get("/risk", self.get_current_risk)
        app.router.add_get("/risk/{asset}", self.get_current_risk)
        app.router.add_get("/calendar", self.get_calendar)
        app.router.add_get("/calendar/today", self.get_calendar_today)
        app.router.add_get("/calendar/week", self.get_calendar_week)
        app.router.add_get("/recommendation", self.get_recommendation)
        app.router.add_get("/recommendation/{asset}", self.get_recommendation)
        app.router.add_get("/health", self.health_check)
        return app

    async def get_current_risk(self, request: web.Request) -> web.Response:
        asset = request.match_info.get("asset")
        current_time = datetime.now()
        risks = self.risk_aggregator.get_current_risk(current_time)

        if asset:
            asset = asset.upper()
            if asset not in risks:
                return web.json_response(
                    {"error": f"Unknown asset: {asset}"},
                    status=404,
                )
            risk = risks[asset]
            return web.json_response(self._serialize_asset_risk(risk))

        return web.json_response({
            asset: self._serialize_asset_risk(risk)
            for asset, risk in risks.items()
        })

    async def get_calendar(self, request: web.Request) -> web.Response:
        view_type = request.query.get("view", "today")
        if view_type == "week":
            return await self.get_calendar_week(request)
        return await self.get_calendar_today(request)

    async def get_calendar_today(self, request: web.Request) -> web.Response:
        current_time = datetime.now()
        calendar_text = self.calendar_view.generate_today(current_time)
        return web.json_response({
            "view": "today",
            "date": current_time.strftime("%Y-%m-%d"),
            "calendar": calendar_text,
        })

    async def get_calendar_week(self, request: web.Request) -> web.Response:
        current_time = datetime.now()
        calendar_text = self.calendar_view.generate_week(current_time)
        return web.json_response({
            "view": "week",
            "start_date": current_time.strftime("%Y-%m-%d"),
            "calendar": calendar_text,
        })

    async def get_recommendation(self, request: web.Request) -> web.Response:
        asset = request.match_info.get("asset")
        current_time = datetime.now()
        risks = self.risk_aggregator.get_current_risk(current_time)

        if asset:
            asset = asset.upper()
            if asset not in risks:
                return web.json_response(
                    {"error": f"Unknown asset: {asset}"},
                    status=404,
                )
            risk = risks[asset]
            recommendation = self.recommendation_engine.get_recommendation(risk)
            return web.json_response(self._serialize_recommendation(recommendation))

        recommendations = self.recommendation_engine.get_all_recommendations(risks)
        return web.json_response({
            asset: self._serialize_recommendation(rec)
            for asset, rec in recommendations.items()
        })

    async def health_check(self, request: web.Request) -> web.Response:
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "events_loaded": len(self.risk_aggregator.events),
        })

    def _serialize_asset_risk(self, risk: AssetRisk) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "asset": risk.asset,
            "score": risk.score,
            "status": risk.status,
        }
        if risk.next_event:
            result["next_event"] = {
                "id": risk.next_event.id,
                "title": risk.next_event.title,
                "scheduled_time": risk.next_event.scheduled_time.isoformat(),
            }
        return result

    def _serialize_recommendation(self, rec: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "asset": rec.asset,
            "risk_level": rec.risk_level,
            "action": rec.action,
            "guidance": rec.guidance,
        }
        if rec.next_event:
            result["next_event"] = {
                "id": rec.next_event.id,
                "title": rec.next_event.title,
                "scheduled_time": rec.next_event.scheduled_time.isoformat(),
            }
        return result


def create_api(
    risk_aggregator: Optional[RiskAggregator] = None,
    config: Optional[Config] = None,
) -> EDRRApi:
    return EDRRApi(risk_aggregator, config)


def run_server(
    api: Optional[EDRRApi] = None,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    api = api or EDRRApi()
    app = api.create_app()
    web.run_app(app, host=host, port=port)
