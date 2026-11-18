# START_MODULE_CONTRACT
#   PURPOSE: FastAPI application factory and ASGI entrypoint.
#   SCOPE: Router wiring, CORS, error handlers, health endpoint, shared Keitaro client lifespan.
#   DEPENDS: M-BACKEND-CORE
#   LINKS: M-BACKEND-API, V-M-BACKEND-API
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   lifespan - opens / closes the shared Keitaro http client
#   create_app - builds the FastAPI app
#   app - ASGI app used by uvicorn (app.main:app)
# END_MODULE_MAP
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import campaigns, editor, reference
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.integrations.keitaro.client import create_http_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # START_BLOCK_LIFESPAN
    app.state.keitaro_http = create_http_client()
    try:
        yield
    finally:
        await app.state.keitaro_http.aclose()
    # END_BLOCK_LIFESPAN


def create_app() -> FastAPI:
    app = FastAPI(title="Keitaro Campaign Tool", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)

    @app.get("/api/health", tags=["health"], operation_id="health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(reference.router)
    app.include_router(campaigns.router)
    app.include_router(editor.router)
    return app


app = create_app()
