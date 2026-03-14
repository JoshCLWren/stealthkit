"""Tests for stealthkit.ratelimit module."""

import asyncio

import pytest

from stealthkit.ratelimit import AdaptiveRateLimiter, RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_init_default_values(self):
        """Test default initialization."""
        limiter = RateLimiter(name="test")
        assert limiter.name == "test"
        assert limiter.max_per_hour == 10000
        assert limiter.max_per_day == 100000
        assert limiter.min_interval == 0.5
        assert limiter.max_backoff == 3600.0

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        limiter = RateLimiter(
            name="test",
            max_per_hour=100,
            max_per_day=1000,
            min_interval=1.0,
            max_backoff=60.0,
        )
        assert limiter.max_per_hour == 100
        assert limiter.max_per_day == 1000
        assert limiter.min_interval == 1.0
        assert limiter.max_backoff == 60.0

    @pytest.mark.asyncio
    async def test_wait_if_needed_basic(self):
        """Test basic wait_if_needed functionality."""
        limiter = RateLimiter(name="test", max_per_hour=10000, min_interval=0.01)

        await limiter.wait_if_needed()

        assert len(limiter.hourly_requests) == 1
        assert len(limiter.daily_requests) == 1

    @pytest.mark.asyncio
    async def test_min_interval_enforcement(self):
        """Test that minimum interval is enforced."""
        limiter = RateLimiter(name="test", min_interval=0.1)

        await limiter.wait_if_needed()
        await limiter.wait_if_needed()

        assert limiter._last_request_time is not None

    @pytest.mark.asyncio
    async def test_record_error(self):
        """Test recording errors."""
        limiter = RateLimiter(name="test")

        limiter.record_error()

        assert limiter.consecutive_errors == 1
        assert limiter.backoff_until is not None

        limiter.record_error()

        assert limiter.consecutive_errors == 2

    def test_reset_errors(self):
        """Test resetting errors."""
        limiter = RateLimiter(name="test")

        limiter.record_error()
        limiter.record_error()

        assert limiter.consecutive_errors == 2
        assert limiter.backoff_until is not None

        limiter.reset_errors()

        assert limiter.consecutive_errors == 0
        assert limiter.backoff_until is None

    def test_get_status(self):
        """Test getting limiter status."""
        limiter = RateLimiter(name="test", max_per_hour=100, max_per_day=1000)

        limiter.record_error()
        status = limiter.get_status()

        assert status["name"] == "test"
        assert status["hourly_count"] == 0
        assert status["daily_count"] == 0
        assert status["hourly_limit"] == 100
        assert status["daily_limit"] == 1000
        assert status["consecutive_errors"] == 1
        assert status["in_backoff"] is True

    @pytest.mark.asyncio
    async def test_backoff_wait(self):
        """Test that backoff causes wait."""
        limiter = RateLimiter(name="test", max_backoff=0.1)

        limiter.record_error()

        assert limiter.backoff_until is not None

        start = asyncio.get_event_loop().time()
        await limiter.wait_if_needed()
        elapsed = asyncio.get_event_loop().time() - start

        assert elapsed > 0


class TestAdaptiveRateLimiter:
    """Tests for AdaptiveRateLimiter class."""

    def test_init_default_values(self):
        """Test default initialization."""
        limiter = AdaptiveRateLimiter(name="test")
        assert limiter.base_interval == 1.0
        assert limiter.min_interval == 1.0
        assert limiter.decrease_factor == 2.0
        assert limiter.increase_factor == 0.9

    def test_record_error_increases_interval(self):
        """Test that errors increase the interval."""
        limiter = AdaptiveRateLimiter(name="test", base_interval=1.0)

        limiter.record_error()

        assert limiter.min_interval == 2.0

        limiter.record_error()

        assert limiter.min_interval == 4.0

    def test_reset_errors_decreases_interval(self):
        """Test that success decreases the interval."""
        limiter = AdaptiveRateLimiter(
            name="test",
            base_interval=1.0,
            min_interval_floor=0.1,
        )

        limiter.record_error()
        limiter.record_error()
        limiter.record_error()

        assert limiter.min_interval == 8.0

        limiter.reset_errors()

        assert limiter.min_interval == 7.2

    def test_interval_bounds(self):
        """Test that interval stays within bounds."""
        limiter = AdaptiveRateLimiter(
            name="test",
            base_interval=1.0,
            max_interval_ceiling=10.0,
            min_interval_floor=0.1,
        )

        for _ in range(20):
            limiter.record_error()

        assert limiter.min_interval <= 10.0

        for _ in range(20):
            limiter.reset_errors()

        assert limiter.min_interval >= 0.1
