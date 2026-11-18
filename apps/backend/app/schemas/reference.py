# START_MODULE_CONTRACT
#   PURPOSE: Reference-data DTOs for creator form selectors.
#   SCOPE: Offer, Domain, Group, TrafficSource, CreatorDefaults.
#   DEPENDS: none
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   OfferOut         - offer
#   DomainOut        - domain
#   GroupOut         - campaign group
#   TrafficSourceOut - traffic source
#   CreatorDefaults  - default domain/group/source ids from env
# END_MODULE_MAP
from pydantic import BaseModel


class OfferOut(BaseModel):
    id: int
    name: str
    state: str
    country: list[str] = []
    group: str | None = None


class DomainOut(BaseModel):
    id: int
    name: str
    state: str
    is_ssl: bool


class GroupOut(BaseModel):
    id: int
    name: str


class TrafficSourceOut(BaseModel):
    id: int
    name: str
    state: str


class CreatorDefaults(BaseModel):
    domain_id: int | None
    group_id: int | None
    traffic_source_id: int | None
    geo_redirect_url: str
    campaign_name_prefix: str
