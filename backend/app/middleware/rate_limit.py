"""
Rate limiting middleware for API endpoints.
Prevents abuse and ensures fair resource usage.
"""

import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

# Rate limit configuration from environment
DEFAULT_RATE_LIMIT = os.getenv("API_RATE_LIMIT_PER_MINUTE", "60/minute")
STRICT_RATE_LIMIT = os.getenv("API_RATE_LIMIT_STRICT", "10/minute")

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[DEFAULT_RATE_LIMIT],
    storage_uri=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    strategy="fixed-window",
    headers_enabled=True,
)


def rate_limit_exceeded_handler(request, exc):
    """
    Custom handler for rate limit exceeded errors.
    Logs the event and returns appropriate response.
    """
    client_ip = get_remote_address(request)
    logger.warning(
        f"Rate limit exceeded for IP {client_ip} on endpoint {request.url.path}"
    )
    return _rate_limit_exceeded_handler(request, exc)
