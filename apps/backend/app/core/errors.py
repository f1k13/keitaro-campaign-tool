# START_MODULE_CONTRACT
#   PURPOSE: Domain exceptions and their mapping to HTTP responses.
#   SCOPE: Error types shared by services and the HTTP layer.
#   DEPENDS: none
#   LINKS: M-BACKEND-CORE, V-M-BACKEND-CORE
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   AppError - base error with HTTP status and machine-readable code
#   NotFoundError - requested entity does not exist (404)
#   ValidationFailedError - business validation failed (422)
#   UpstreamError - Keitaro API failed or returned an error (502)
#   register_error_handlers - installs JSON handlers on the FastAPI app
# END_MODULE_MAP
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ValidationFailedError(AppError):
    status_code = 422
    code = "validation_failed"


class UpstreamError(AppError):
    status_code = 502
    code = "keitaro_error"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message, "code": exc.code})
