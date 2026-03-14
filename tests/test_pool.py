"""Tests for stealthkit.pool module."""

import pytest

from stealthkit.pool import PagePool


class TestPagePool:
    """Tests for PagePool class."""

    def test_init_valid_size(self):
        """Test PagePool initialization with valid size."""
        pool = PagePool(size=5, browser_context=None)
        assert pool.size == 5
        assert pool.initialized is False

    def test_init_invalid_size(self):
        """Test PagePool initialization with invalid size."""
        with pytest.raises(ValueError, match="size must be at least 1"):
            PagePool(size=0, browser_context=None)

        with pytest.raises(ValueError, match="size must be at least 1"):
            PagePool(size=-1, browser_context=None)

    def test_available_count_before_init(self):
        """Test available_count returns 0 before initialization."""
        pool = PagePool(size=3, browser_context=None)
        assert pool.available_count == 0


class TestPagePoolIntegration:
    """Integration tests for PagePool with real browser."""

    @pytest.mark.asyncio
    async def test_initialize_creates_pages(self):
        """Test that initialize creates the expected number of pages."""
        from stealthkit.browser import StealthBrowser

        async with StealthBrowser() as browser:
            pool = PagePool(size=3, browser_context=browser.context)
            await pool.initialize()
            assert pool.initialized is True
            assert pool.available_count == 3
            await pool.close_all()

    @pytest.mark.asyncio
    async def test_get_and_release_page(self):
        """Test getting and releasing pages."""
        from stealthkit.browser import StealthBrowser

        async with StealthBrowser() as browser:
            pool = PagePool(size=2, browser_context=browser.context)
            await pool.initialize()

            page = await pool.get_page()
            assert page is not None
            assert pool.available_count == 1

            await pool.release_page(page)
            assert pool.available_count == 2

            await pool.close_all()

    @pytest.mark.asyncio
    async def test_acquire_context_manager(self):
        """Test acquire context manager."""
        from stealthkit.browser import StealthBrowser

        async with StealthBrowser() as browser:
            pool = PagePool(size=2, browser_context=browser.context)
            await pool.initialize()

            async with pool.acquire() as page:
                assert page is not None
                assert pool.available_count == 1

            assert pool.available_count == 2
            await pool.close_all()

    @pytest.mark.asyncio
    async def test_get_page_without_init_raises(self):
        """Test that get_page raises error without initialization."""
        from stealthkit.browser import StealthBrowser

        async with StealthBrowser() as browser:
            pool = PagePool(size=2, browser_context=browser.context)

            with pytest.raises(RuntimeError, match="Pool not initialized"):
                await pool.get_page()
