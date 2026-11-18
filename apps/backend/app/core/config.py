# START_MODULE_CONTRACT
#   PURPOSE: Typed application settings loaded from environment / .env.
#   SCOPE: Keitaro connection, campaign defaults and name prefix, database URL, CORS.
#   DEPENDS: none
#   LINKS: M-BACKEND-CORE, V-M-BACKEND-CORE
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   ROOT_ENV_FILE - path to the repository-root .env
#   Settings      - pydantic-settings model with all runtime configuration
#   get_settings  - cached Settings accessor used as a FastAPI dependency
# END_MODULE_MAP
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root .env (apps/backend/app/core/config.py -> 4 levels up). In Docker the file is absent
# and values come from docker-compose env_file; pydantic-settings skips missing files.
_HERE = Path(__file__).resolve()
ROOT_ENV_FILE = _HERE.parents[4] / ".env" if len(_HERE.parents) > 4 else Path(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    keitaro_base_url: str = Field(description="Tracker URL, e.g. https://tracker.example")
    keitaro_api_key: str
    keitaro_timeout_seconds: float = 30.0
    keitaro_cache_ttl_seconds: float = Field(
        default=60.0, description="TTL for cached campaign/offer lists; 0 disables"
    )

    keitaro_default_domain_id: int | None = None
    keitaro_default_group_id: int | None = None
    keitaro_default_traffic_source_id: int | None = None
    keitaro_geo_redirect_url: str = "https://www.google.com"
    campaign_name_prefix: str = Field(default="", description="Prepended to every created campaign name")

    database_url: str = "postgresql+asyncpg://keitaro:keitaro@localhost:5433/keitaro"
    cors_origins: str = "http://localhost:5173"

    @property
    def keitaro_api_url(self) -> str:
        return self.keitaro_base_url.rstrip("/") + "/admin_api/v1"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# START_CONTRACT: get_settings
#   PURPOSE: Return the process-wide Settings instance.
#   INPUTS: none
#   OUTPUTS: { Settings - parsed configuration }
#   SIDE_EFFECTS: reads environment and .env once
# END_CONTRACT: get_settings
@lru_cache
def get_settings() -> Settings:
    return Settings()
