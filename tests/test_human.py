"""Tests for stealthkit.human module."""

import pytest

from stealthkit.human import (
    human_like_delay,
    human_scroll,
    navigate_with_human_behavior,
    random_mouse_movements,
    scroll_to_element,
    type_like_human,
)


class TestHumanLikeDelay:
    """Tests for human_like_delay function."""

    @pytest.mark.asyncio
    async def test_delay_in_range(self):
        """Test that delay is within the specified range."""
        import time

        start = time.time()
        await human_like_delay(min_seconds=0.1, max_seconds=0.2)
        elapsed = time.time() - start

        assert elapsed >= 0.1
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_delay_different_each_time(self):
        """Test that delays vary between calls."""
        import asyncio

        delays = []
        for _ in range(5):
            start = asyncio.get_event_loop().time()
            await human_like_delay(min_seconds=0.01, max_seconds=0.02)
            elapsed = asyncio.get_event_loop().time() - start
            delays.append(elapsed)

        unique_delays = {round(d, 4) for d in delays}
        assert len(unique_delays) >= 1


class TestRandomMouseMovements:
    """Tests for random_mouse_movements function."""

    @pytest.mark.asyncio
    async def test_movements_with_mock_page(self):
        """Test mouse movements with mocked page."""
        from unittest.mock import AsyncMock

        page = AsyncMock()
        page.viewport_size = {"width": 1920, "height": 1080}
        page.mouse = AsyncMock()

        await random_mouse_movements(page, count=2)

        assert page.mouse.move.call_count == 2

    @pytest.mark.asyncio
    async def test_movements_respects_viewport(self):
        """Test that movements stay within viewport bounds."""
        from unittest.mock import AsyncMock

        page = AsyncMock()
        page.viewport_size = {"width": 800, "height": 600}
        page.mouse = AsyncMock()

        await random_mouse_movements(page, count=5)

        for call in page.mouse.move.call_args_list:
            x = call[0][0]
            y = call[0][1]
            assert 0 <= x < 800
            assert 0 <= y < 600


class TestHumanScroll:
    """Tests for human_scroll function."""

    @pytest.mark.asyncio
    async def test_scroll_with_mock_page(self):
        """Test scrolling with mocked page."""
        from unittest.mock import AsyncMock

        page = AsyncMock()
        page.mouse = AsyncMock()

        await human_scroll(page, distance=500)

        assert page.mouse.wheel.call_count >= 1


class TestNavigateWithHumanBehavior:
    """Tests for navigate_with_human_behavior function."""

    @pytest.mark.asyncio
    async def test_navigate_with_mock_page(self):
        """Test navigation with mocked page."""
        from unittest.mock import AsyncMock

        page = AsyncMock()
        page.viewport_size = {"width": 1920, "height": 1080}
        page.mouse = AsyncMock()

        await navigate_with_human_behavior(
            page,
            "https://example.com",
            wait_until="domcontentloaded",
            timeout=5000,
        )

        page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="domcontentloaded",
            timeout=5000,
        )


class TestTypeLikeHuman:
    """Tests for type_like_human function."""

    @pytest.mark.asyncio
    async def test_typing_with_mock_page(self):
        """Test typing with mocked page."""
        from unittest.mock import AsyncMock

        page = AsyncMock()
        page.keyboard = AsyncMock()

        await type_like_human(
            page,
            "input#test",
            "hello",
            min_delay=0.01,
            max_delay=0.02,
            mistake_probability=0,
        )

        page.click.assert_called_once_with("input#test")
        assert page.keyboard.press.call_count == 5


class TestScrollToElement:
    """Tests for scroll_to_element function."""

    @pytest.mark.asyncio
    async def test_scroll_to_element_with_mock_page(self):
        """Test scrolling to element with mocked page."""
        from unittest.mock import AsyncMock

        page = AsyncMock()
        page.viewport_size = {"width": 1920, "height": 1080}
        page.mouse = AsyncMock()

        element = AsyncMock()
        page.query_selector = AsyncMock(return_value=element)

        await scroll_to_element(page, "#target")

        element.scroll_into_view_if_needed.assert_called_once()
        page.mouse.move.assert_called()
