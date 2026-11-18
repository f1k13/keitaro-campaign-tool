# START_MODULE_CONTRACT
#   PURPOSE: Public HTTP API DTOs (request/response bodies) - the API contract.
#   SCOPE: Pydantic models exported into contracts/openapi.json.
#   DEPENDS: none
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   campaigns - create request, created response, campaign list DTOs
#   editor    - editor view, stream/offer rows, offer mutation requests, change log DTOs
#   reference - offers / domains / groups / traffic sources / defaults DTOs
# END_MODULE_MAP
from app.schemas import campaigns, editor, reference

__all__ = ["campaigns", "editor", "reference"]
