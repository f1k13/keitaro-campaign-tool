# START_MODULE_CONTRACT
#   PURPOSE: Pydantic models of the Keitaro Admin API objects this tool reads.
#   SCOPE: Only fields the tool uses; unknown fields are ignored.
#   DEPENDS: none
#   LINKS: M-KEITARO-CLIENT, V-M-KEITARO-CLIENT
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   KCampaign      - campaign
#   KStreamFilter  - stream filter
#   KStreamOffer   - offer inside a stream with share
#   KStream        - stream
#   KOffer         - offer
#   KDomain        - domain
#   KGroup         - campaign group
#   KTrafficSource - traffic source
#   KReportRow     - report row grouped by stream_id + offer_id
# END_MODULE_MAP
from typing import Any

from pydantic import BaseModel, ConfigDict


class _K(BaseModel):
    model_config = ConfigDict(extra="ignore")


class KCampaign(_K):
    id: int
    alias: str
    name: str
    state: str
    type: str
    group_id: int | None = None
    domain_id: int | None = None
    traffic_source_id: int | None = None
    domain: str | None = None
    group: str | None = None
    created_at: str | None = None


class KStreamFilter(_K):
    name: str
    mode: str
    payload: Any = None


class KStreamOffer(_K):
    id: int | None = None
    offer_id: int
    share: int
    state: str = "active"


class KStream(_K):
    id: int
    campaign_id: int
    type: str
    name: str | None = None
    position: int
    state: str
    schema_: str | None = None
    action_type: str | None = None
    action_payload: str | None = None
    filters: list[KStreamFilter] = []
    offers: list[KStreamOffer] = []

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "KStream":
        return cls.model_validate({**data, "schema_": data.get("schema")})


class KOffer(_K):
    id: int
    name: str
    state: str
    country: list[str] | None = None
    group: str | None = None


class KDomain(_K):
    id: int
    name: str
    state: str
    is_ssl: bool = False


class KGroup(_K):
    id: int
    name: str


class KTrafficSource(_K):
    id: int
    name: str
    state: str


class KReportRow(_K):
    stream_id: int | None = None
    offer_id: int | None = None
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0
    profit: float = 0
