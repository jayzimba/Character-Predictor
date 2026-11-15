"""OpenAPI docs stay on in development and are off when APP_DEBUG is false."""


def openapi_urls(*, debug: bool) -> dict[str, str | None]:
    if debug:
        return {
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json",
        }
    return {"docs_url": None, "redoc_url": None, "openapi_url": None}
