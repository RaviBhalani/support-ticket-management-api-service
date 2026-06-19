import uuid
import structlog


class StructlogContextMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        structlog.contextvars.clear_contextvars()
        client = scope.get("client")
        structlog.contextvars.bind_contextvars(
            request_id=uuid.uuid4().hex,
            method=scope.get("method"),
            path=scope.get("path"),
            client_host=client[0] if client else None,
        )
        try:
            await self.app(scope, receive, send)
        finally:
            structlog.contextvars.clear_contextvars()
