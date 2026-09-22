import time
from collections import defaultdict
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings

# In-memory IP tracking storage
_ip_requests_store: Dict[str, List[float]] = defaultdict(list)


def reset_rate_limits() -> None:
    _ip_requests_store.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # Only rate-limit API routes
        path = request.url.path
        if not (path.startswith("/expenses") or path.startswith("/summary")):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.rate_limit_window_seconds
        max_requests = settings.rate_limit_requests

        # Clean old timestamps outside the sliding window
        window_start = now - window
        timestamps = [ts for ts in _ip_requests_store[client_ip] if ts > window_start]

        if len(timestamps) >= max_requests:
            retry_after = int(window - (now - timestamps[0])) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        timestamps.append(now)
        _ip_requests_store[client_ip] = timestamps

        return await call_next(request)
