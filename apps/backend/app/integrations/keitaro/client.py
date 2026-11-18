# START_MODULE_CONTRACT
#   PURPOSE: Async client for the Keitaro Admin API v1 (Api-Key auth).
#   SCOPE: Thin typed wrappers over the endpoints the tool needs; no business rules. Campaign and offer
#          lists are cached for KEITARO_CACHE_TTL_SECONDS; stream reads and reports are never cached.
#   DEPENDS: M-BACKEND-CORE
#   LINKS: M-KEITARO-CLIENT, V-M-KEITARO-CLIENT
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   log                - module logger
#   KeitaroClient      - typed wrappers over Keitaro Admin API endpoints (lists cached with TTL)
#   create_http_client - shared keep-alive httpx client (created once in the app lifespan)
#   get_keitaro_client - FastAPI dependency wrapping the shared http client
# END_MODULE_MAP
import logging
from typing import Any

import httpx
from fastapi import Request

from app.core.config import get_settings
from app.core.errors import NotFoundError, UpstreamError
from app.integrations.keitaro.cache import TTLCache, keitaro_cache
from app.integrations.keitaro.models import (
    KCampaign,
    KDomain,
    KGroup,
    KOffer,
    KReportRow,
    KStream,
    KTrafficSource,
)

log = logging.getLogger("keitaro")


class KeitaroClient:
    def __init__(self, http: httpx.AsyncClient, cache: TTLCache | None = None, cache_ttl: float = 0) -> None:
        self._http = http
        self._cache = cache or TTLCache()
        self._ttl = cache_ttl

    # START_BLOCK_REQUEST
    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            resp = await self._http.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            log.warning("[Keitaro][request][BLOCK_REQUEST] %s %s failed: %s", method, path, exc)
            raise UpstreamError(f"Keitaro недоступен: {exc}") from exc
        if resp.status_code == 404:
            raise NotFoundError(f"Keitaro: объект не найден ({path})")
        if resp.status_code >= 400:
            try:
                body = resp.json()
                message = body.get("error") or body
            except ValueError:
                message = resp.text[:300]
            log.warning(
                "[Keitaro][request][BLOCK_REQUEST] %s %s -> %s %s", method, path, resp.status_code, message
            )
            raise UpstreamError(f"Keitaro {resp.status_code}: {message}")
        if not resp.content:
            return None
        return resp.json()

    # END_BLOCK_REQUEST

    # --- reference data -------------------------------------------------
    async def list_offers(self) -> list[KOffer]:
        async def load() -> list[KOffer]:
            return [KOffer.model_validate(o) for o in await self._request("GET", "/offers")]

        result: list[KOffer] = await self._cache.get_or_load("offers", self._ttl, load)
        return result

    # START_CONTRACT: get_offer
    #   PURPOSE: Look up one offer by id; tolerate API keys without read access to offers.
    #   INPUTS: { offer_id: int }
    #   OUTPUTS: { KOffer | None - None when Keitaro answers 403 (offer exists, not readable) }
    #   SIDE_EFFECTS: raises NotFoundError on 404, UpstreamError on other failures
    # END_CONTRACT: get_offer
    async def get_offer(self, offer_id: int) -> KOffer | None:
        try:
            return KOffer.model_validate(await self._request("GET", f"/offers/{offer_id}"))
        except UpstreamError as exc:
            if exc.message.startswith("Keitaro 403"):
                return None
            raise

    async def list_domains(self) -> list[KDomain]:
        return [KDomain.model_validate(o) for o in await self._request("GET", "/domains")]

    async def list_campaign_groups(self) -> list[KGroup]:
        data = await self._request("GET", "/groups", params={"type": "campaigns"})
        return [KGroup.model_validate(o) for o in data]

    async def list_traffic_sources(self) -> list[KTrafficSource]:
        return [KTrafficSource.model_validate(o) for o in await self._request("GET", "/traffic_sources")]

    # --- campaigns ------------------------------------------------------
    async def list_campaigns(self) -> list[KCampaign]:
        async def load() -> list[KCampaign]:
            return [KCampaign.model_validate(o) for o in await self._request("GET", "/campaigns")]

        result: list[KCampaign] = await self._cache.get_or_load("campaigns", self._ttl, load)
        return result

    async def get_campaign(self, campaign_id: int) -> KCampaign:
        return KCampaign.model_validate(await self._request("GET", f"/campaigns/{campaign_id}"))

    async def create_campaign(self, payload: dict[str, Any]) -> KCampaign:
        try:
            return KCampaign.model_validate(await self._request("POST", "/campaigns", json=payload))
        finally:
            self._cache.invalidate("campaigns")

    async def delete_campaign(self, campaign_id: int) -> None:
        try:
            await self._request("DELETE", f"/campaigns/{campaign_id}")
        finally:
            self._cache.invalidate("campaigns")

    # --- streams --------------------------------------------------------
    async def list_streams(self, campaign_id: int) -> list[KStream]:
        data = await self._request("GET", f"/campaigns/{campaign_id}/streams")
        return [KStream.from_api(s) for s in data]

    async def get_stream(self, stream_id: int) -> KStream:
        return KStream.from_api(await self._request("GET", f"/streams/{stream_id}"))

    async def create_stream(self, payload: dict[str, Any]) -> KStream:
        return KStream.from_api(await self._request("POST", "/streams", json=payload))

    async def update_stream(self, stream_id: int, payload: dict[str, Any]) -> KStream:
        return KStream.from_api(await self._request("PUT", f"/streams/{stream_id}", json=payload))

    # --- reports --------------------------------------------------------
    # START_CONTRACT: offer_stats
    #   PURPOSE: Clicks/conversions/revenue/profit per (stream, offer) of one campaign.
    #   INPUTS: { campaign_id: int, interval: str - Keitaro range interval, timezone: str }
    #   OUTPUTS: { list[KReportRow] }
    #   SIDE_EFFECTS: none (read-only report)
    # END_CONTRACT: offer_stats
    async def offer_stats(self, campaign_id: int, interval: str, timezone: str) -> list[KReportRow]:
        body = {
            "range": {"interval": interval, "timezone": timezone},
            "dimensions": ["stream_id", "offer_id"],
            "measures": ["clicks", "conversions", "revenue", "profit"],
            "filters": [{"name": "campaign_id", "operator": "EQUALS", "expression": campaign_id}],
            "limit": 1000,
        }
        data = await self._request("POST", "/report/build", json=body)
        return [KReportRow.model_validate(r) for r in data.get("rows", [])]


# START_CONTRACT: create_http_client
#   PURPOSE: Build the process-wide keep-alive httpx client for Keitaro (one TLS connection pool).
#   INPUTS: none
#   OUTPUTS: { httpx.AsyncClient - caller (app lifespan) must aclose() it }
#   SIDE_EFFECTS: none until first request
# END_CONTRACT: create_http_client
def create_http_client() -> httpx.AsyncClient:
    settings = get_settings()
    return httpx.AsyncClient(
        base_url=settings.keitaro_api_url,
        headers={"Api-Key": settings.keitaro_api_key, "Accept": "application/json"},
        timeout=settings.keitaro_timeout_seconds,
        limits=httpx.Limits(max_keepalive_connections=10, keepalive_expiry=60),
    )


# START_CONTRACT: get_keitaro_client
#   PURPOSE: Provide a KeitaroClient over the shared http client and the process-wide list cache.
#   INPUTS: { request: Request - app.state.keitaro_http set by the lifespan }
#   OUTPUTS: { KeitaroClient }
#   SIDE_EFFECTS: none
# END_CONTRACT: get_keitaro_client
async def get_keitaro_client(request: Request) -> KeitaroClient:
    http: httpx.AsyncClient = request.app.state.keitaro_http
    return KeitaroClient(http, keitaro_cache, get_settings().keitaro_cache_ttl_seconds)
