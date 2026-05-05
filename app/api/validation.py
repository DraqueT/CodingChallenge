from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        del request
        details = []
        for error in exc.errors():
            field_path = _format_location(error.get("loc", ()))
            details.append(
                {
                    "field": field_path,
                    "issue": error.get("msg", "Invalid value"),
                }
            )

        return JSONResponse(
            status_code=400,
            content={
                "error": "VALIDATION_ERROR",
                "message": details[0]["issue"] if details else "Validation failed",
                "details": details,
            },
        )


def _format_location(location: tuple[object, ...]) -> str:
    parts: list[str] = []
    for token in location:
        if token == "body":
            continue
        if isinstance(token, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{token}]"
            else:
                parts.append(f"[{token}]")
        else:
            parts.append(str(token))
    return ".".join(parts)
