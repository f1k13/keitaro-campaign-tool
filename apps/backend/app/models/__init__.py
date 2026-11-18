# START_MODULE_CONTRACT
#   PURPOSE: ORM models persisted in PostgreSQL (local history of tool actions).
#   SCOPE: created_campaigns and offer_changes tables.
#   DEPENDS: M-DB
#   LINKS: M-DB, V-M-DB
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   CreatedCampaign - campaign created through the creator
#   OfferChange - audit row for each offer edit applied to a Keitaro stream
# END_MODULE_MAP
from app.models.campaign import CreatedCampaign
from app.models.offer_change import OfferChange

__all__ = ["CreatedCampaign", "OfferChange"]
