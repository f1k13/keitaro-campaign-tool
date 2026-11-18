# START_MODULE_CONTRACT
#   PURPOSE: Async client for the Keitaro Admin API v1 (Api-Key auth).
#   SCOPE: Thin typed wrappers over the endpoints the tool needs; no business rules.
#   DEPENDS: M-BACKEND-CORE
#   LINKS: M-KEITARO-CLIENT, V-M-KEITARO-CLIENT
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   log                - module logger
#   KeitaroClient      - typed wrappers over Keitaro Admin API endpoints
#   get_keitaro_client - FastAPI dependency yielding a client per request
# END_MODULE_MAP
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.errors import NotFoundError, UpstreamError
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
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

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
        return [KOffer.model_validate(o) for o in await self._request("GET", "/offers")]

    async def list_domains(self) -> list[KDomain]:
        return [KDomain.model_validate(o) for o in await self._request("GET", "/domains")]

    async def list_campaign_groups(self) -> list[KGroup]:
        data = await self._request("GET", "/groups", params={"type": "campaigns"})
        return [KGroup.model_validate(o) for o in data]

    async def list_traffic_sources(self) -> list[KTrafficSource]:
        return [KTrafficSource.model_validate(o) for o in await self._request("GET", "/traffic_sources")]

    # --- campaigns ------------------------------------------------------
    async def list_campaigns(self) -> list[KCampaign]:
        return [KCampaign.model_validate(o) for o in await self._request("GET", "/campaigns")]

    async def get_campaign(self, campaign_id: int) -> KCampaign:
        return KCampaign.model_validate(await self._request("GET", f"/campaigns/{campaign_id}"))

    async def create_campaign(self, payload: dict[str, Any]) -> KCampaign:
        return KCampaign.model_validate(await self._request("POST", "/campaigns", json=payload))

    async def delete_campaign(self, campaign_id: int) -> None:
        await self._request("DELETE", f"/campaigns/{campaign_id}")

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


# START_CONTRACT: get_keitaro_client
#   PURPOSE: Provide a KeitaroClient bound to configured URL and API key.
#   INPUTS: none
#   OUTPUTS: { AsyncIterator[KeitaroClient] }
#   SIDE_EFFECTS: opens and closes an httpx.AsyncClient
# END_CONTRACT: get_keitaro_client
async def get_keitaro_client() -> AsyncIterator[KeitaroClient]:
    settings = get_settings()
    async with httpx.AsyncClient(
        base_url=settings.keitaro_api_url,
        headers={"Api-Key": settings.keitaro_api_key, "Accept": "application/json"},
        timeout=settings.keitaro_timeout_seconds,
    ) as http:
        yield KeitaroClient(http)
