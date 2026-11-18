# START_MODULE_CONTRACT
#   PURPOSE: Keitaro Admin API integration package.
#   SCOPE: Re-exports the client and wire models.
#   DEPENDS: M-BACKEND-CORE
#   LINKS: M-KEITARO-CLIENT, V-M-KEITARO-CLIENT
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   KeitaroClient - async HTTP client for Keitaro Admin API v1
#   get_keitaro_client - FastAPI dependency
# END_MODULE_MAP
from app.integrations.keitaro.client import KeitaroClient, get_keitaro_client

__all__ = ["KeitaroClient", "get_keitaro_client"]
