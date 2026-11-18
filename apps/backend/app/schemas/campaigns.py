# START_MODULE_CONTRACT
#   PURPOSE: Campaign creator and campaign list DTOs.
#   SCOPE: CampaignCreate request, CampaignCreated response, CampaignOut, CreatedCampaignOut.
#   DEPENDS: none
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   CampaignCreate - creator input (name, ISO country, offer, optional domain/group/source)
#   CampaignCreated - creator output with Keitaro ids and the campaign URL
#   CampaignOut - campaign row for the editor picker
#   CreatedCampaignOut - local history row
# END_MODULE_MAP
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    country: str = Field(description="ISO 3166-1 alpha-2 country code, e.g. US")
    offer_id: int = Field(gt=0)
    domain_id: int | None = Field(default=None, gt=0)
    group_id: int | None = Field(default=None, gt=0)
    traffic_source_id: int | None = Field(default=None, gt=0)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Название не может быть пустым")
        return v

    @field_validator("country")
    @classmethod
    def _country(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 2 or not v.isalpha() or not v.isascii():
            raise ValueError("Гео должно быть двухбуквенным ISO-кодом страны, например US")
        return v


class CampaignCreated(BaseModel):
    campaign_id: int
    alias: str
    name: str
    url: str | None
    country: str
    offer_id: int
    domain_id: int
    group_id: int
    traffic_source_id: int
    geo_stream_id: int
    offer_stream_id: int


class CampaignOut(BaseModel):
    id: int
    name: str
    alias: str
    state: str
    group: str | None
    domain: str | None
    created_at: str | None
    created_here: bool


class CreatedCampaignOut(BaseModel):
    keitaro_campaign_id: int
    name: str
    alias: str
    country: str
    offer_id: int
    url: str | None
    created_at: datetime
