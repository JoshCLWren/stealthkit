"""Rate limiting with exponential backoff for web scraping.

This module provides RateLimiter for request throttling:
- Track requests per hour/day
- Automatic exponential backoff on errors
- Configurable limits

Usage:
    from stealthkit.ratelimit import RateLimiter

    limiter = RateLimiter(max_per_hour=1000, max_per_day=10000)

    async def make_request(url):
        await limiter.wait_if_needed()
        try:
            response = await fetch(url)
            limiter.reset_errors()
            return response
        except Exception:
            limiter.record_error()
            raise
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RateLimiter:
    """Rate limiter with exponential backoff for web scraping.

    Tracks request counts per hour and per day, and implements
    exponential backoff when errors occur.

    Usage:
        limiter = RateLimiter(name="my-scraper", max_per_hour=1000)

        async def fetch_with_rate_limit(url):
            await limiter.wait_if_needed()
            try:
                response = await httpx.get(url)
                limiter.reset_errors()
                return response
            except Exception:
                limiter.record_error()
                raise

    Attributes:
        name: Identifier for logging
        max_per_hour: Maximum requests per hour (default: 10000)
        max_per_day: Maximum requests per day (default: 100000)
        min_interval: Minimum seconds between requests (default: 0.5)
        max_backoff: Maximum backoff time in seconds (default: 3600)
    """

    name: str
    max_per_hour: int = 10000
    max_per_day: int = 100000
    min_interval: float = 0.5
    max_backoff: float = 3600.0
    hourly_requests: deque = field(default_factory=lambda: deque())
    daily_requests: deque = field(default_factory=lambda: deque())
    backoff_until: datetime | None = None
    consecutive_errors: int = 0
    _last_request_time: float | None = field(default=None, repr=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    def __post_init__(self) -> None:
        """Initialize rate limiter."""
        self._logger = structlog.get_logger(__name__).bind(name=self.name)

    async def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded or in backoff period.

        This method will:
        1. Wait for backoff period if active
        2. Wait for minimum interval since last request
        3. Wait if hourly/daily limits would be exceeded
        """
        async with self._lock:
            now = datetime.now()
            now_ts = time.time()

            if self.backoff_until and now < self.backoff_until:
                wait_seconds = (self.backoff_until - now).total_seconds()
                self._logger.warning(
                    "ratelimit.backoff",
                    wait_seconds=wait_seconds,
                    consecutive_errors=self.consecutive_errors,
                )
                await asyncio.sleep(wait_seconds)

            self._clean_old_requests(now)

            if len(self.hourly_requests) >= self.max_per_hour:
                wait_seconds = 3600 - (now - min(self.hourly_requests)).total_seconds()
                self._logger.warning(
                    "ratelimit.hourly_exceeded",
                    wait_seconds=wait_seconds,
                )
                await asyncio.sleep(max(wait_seconds, 0.1))
                self._clean_old_requests(datetime.now())

            if len(self.daily_requests) >= self.max_per_day:
                wait_seconds = 86400 - (now - min(self.daily_requests)).total_seconds()
                self._logger.warning(
                    "ratelimit.daily_exceeded",
                    wait_seconds=wait_seconds,
                )
                await asyncio.sleep(max(wait_seconds, 0.1))
                self._clean_old_requests(datetime.now())

            if self._last_request_time is not None:
                elapsed = now_ts - self._last_request_time
                if elapsed < self.min_interval:
                    wait_seconds = self.min_interval - elapsed
                    self._logger.debug("ratelimit.min_interval", wait_seconds=wait_seconds)
                    await asyncio.sleep(wait_seconds)

            self.hourly_requests.append(now)
            self.daily_requests.append(now)
            self._last_request_time = time.time()

            self._logger.debug(
                "ratelimit.request_allowed",
                hourly_count=len(self.hourly_requests),
                daily_count=len(self.daily_requests),
            )

    def _clean_old_requests(self, now: datetime) -> None:
        """Remove requests older than tracking windows.

        Args:
            now: Current datetime
        """
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        while self.hourly_requests and self.hourly_requests[0] < hour_ago:
            self.hourly_requests.popleft()

        while self.daily_requests and self.daily_requests[0] < day_ago:
            self.daily_requests.popleft()

    def record_error(self, error: Exception | None = None) -> None:
        """Record an error and increase backoff.

        Exponential backoff formula: min(2^errors, max_backoff)

        Args:
            error: The error that occurred (for logging)
        """
        self.consecutive_errors += 1
        backoff_seconds = min(2**self.consecutive_errors, self.max_backoff)
        self.backoff_until = datetime.now() + timedelta(seconds=backoff_seconds)

        self._logger.warning(
            "ratelimit.error",
            consecutive_errors=self.consecutive_errors,
            backoff_seconds=backoff_seconds,
            error=str(error) if error else None,
        )

    def reset_errors(self) -> None:
        """Reset error counter after successful request."""
        self.consecutive_errors = 0
        self.backoff_until = None

    def get_status(self) -> dict:
        """Get current rate limiter status.

        Returns:
            Dictionary with current status
        """
        now = datetime.now()
        self._clean_old_requests(now)

        return {
            "name": self.name,
            "hourly_count": len(self.hourly_requests),
            "hourly_limit": self.max_per_hour,
            "daily_count": len(self.daily_requests),
            "daily_limit": self.max_per_day,
            "consecutive_errors": self.consecutive_errors,
            "in_backoff": self.backoff_until is not None and self.backoff_until > now,
            "backoff_until": self.backoff_until.isoformat() if self.backoff_until else None,
        }


@dataclass
class AdaptiveRateLimiter(RateLimiter):
    """Rate limiter that adapts based on response times and errors.

    Automatically reduces rate when errors occur and increases
    rate when things are going smoothly.

    Additional Attributes:
        base_interval: Starting minimum interval between requests
        current_interval: Current minimum interval (adjusted based on errors)
        decrease_factor: Factor to increase interval on error
        increase_factor: Factor to decrease interval on success
        min_interval_floor: Minimum possible interval
        max_interval_ceiling: Maximum possible interval
    """

    base_interval: float = 1.0
    decrease_factor: float = 2.0
    increase_factor: float = 0.9
    min_interval_floor: float = 0.1
    max_interval_ceiling: float = 300.0

    def __post_init__(self) -> None:
        """Initialize adaptive rate limiter."""
        super().__post_init__()
        self.min_interval = self.base_interval

    def record_error(self, error: Exception | None = None) -> None:
        """Record error and increase interval.

        Args:
            error: The error that occurred
        """
        super().record_error(error)
        self.min_interval = min(
            self.min_interval * self.decrease_factor,
            self.max_interval_ceiling,
        )

    def reset_errors(self) -> None:
        """Reset errors and decrease interval."""
        super().reset_errors()
        self.min_interval = max(
            self.min_interval * self.increase_factor,
            self.min_interval_floor,
        )
