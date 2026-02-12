"""Simple in-memory rate limiter."""
import os
import time
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 200, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self.clients: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if os.environ.get("TOUCHSTONE_TESTING") == "1":
            return await call_next(request)
        if request.url.path in ("/api/v1/health", "/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        self.clients[client_ip] = [t for t in self.clients[client_ip] if t > now - self.window]
        if len(self.clients[client_ip]) >= self.max_requests:
            return Response(
                content='{"detail":"Rate limit exceeded. Please wait."}',
                status_code=429,
                media_type="application/json",
            )
        self.clients[client_ip].append(now)
        return await call_next(request)
