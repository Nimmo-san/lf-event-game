from fastapi import Request

from slowapi import Limiter
from slowapi.util import get_remote_address


def get_client_ip(request: Request) -> str:
    """The real client IP, trusting Render's X-Forwarded-For header.

    Render's web services aren't directly reachable from the public
    internet — Render's own edge/load balancer is the only path in —
    so X-Forwarded-For here can only have been set by Render itself,
    not spoofed by an arbitrary client.

    Without this, get_remote_address's request.client.host is
    Render's internal proxy IP for every request, since the backend
    runs plain `uvicorn` with no --proxy-headers flag to rewrite it —
    meaning every visitor was effectively sharing one rate-limit
    bucket, regardless of who they actually were.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return get_remote_address(request)


limiter = Limiter(
    key_func=get_client_ip,
)
