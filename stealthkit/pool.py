"""Page pool management for concurrent browser automation.

This module provides PagePool for managing multiple browser pages efficiently:
- Semaphore-backed concurrency control
- Automatic page cleanup and recycling
- Thread-safe page acquisition/release

Usage:
    async with StealthBrowser() as browser:
        pool = PagePool(size=5, browser_context=browser.context)
        await pool.initialize()

        async with pool.acquire() as page:
            await page.goto("https://example.com")
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from playwright.async_api import BrowserContext, Page

logger = structlog.get_logger(__name__)


class PagePool:
    """Manages a pool of Playwright browser pages for concurrent scraping.

    This class provides efficient page reuse with automatic cleanup:
    - Pre-allocates pages on initialization
    - Disables animations for faster rendering
    - Tracks page health (closed pages are replaced)
    - Thread-safe acquisition via asyncio.Queue

    Usage:
        async with StealthBrowser() as browser:
            pool = PagePool(size=5, browser_context=browser.context)
            await pool.initialize()

            page = await pool.get_page()
            try:
                await page.goto("https://example.com")
            finally:
                await pool.release_page(page)

        # Or using context manager:
        async with pool.acquire() as page:
            await page.goto("https://example.com")

    Attributes:
        size: Maximum number of pages in the pool
        browser_context: Playwright browser context
        available_pages: Queue of available pages
        initialized: Whether pool has been initialized
    """

    def __init__(
        self,
        size: int,
        browser_context: BrowserContext | None = None,
    ) -> None:
        """Initialize the page pool.

        Args:
            size: Number of pages to maintain in the pool
            browser_context: Playwright browser context

        Raises:
            ValueError: If size is less than 1
        """
        if size < 1:
            raise ValueError("size must be at least 1")

        self.size = size
        self.browser_context = browser_context
        self.available_pages: asyncio.Queue[Page] = asyncio.Queue(maxsize=size)
        self.initialized = False
        self._logger = structlog.get_logger(__name__).bind(pool_size=size)
        self._semaphore = asyncio.Semaphore(size)

    async def initialize(self) -> None:
        """Initialize the pool with pre-allocated pages.

        Creates all pages upfront for better performance.
        Also closes the initial blank page that Playwright creates.
        """
        if self.browser_context is None:
            raise RuntimeError("browser_context is required for initialization")

        if self.initialized:
            return

        self._logger.debug("pool.initializing", size=self.size)

        await asyncio.gather(*[self._add_page_to_pool() for _ in range(self.size)])

        if self.browser_context.pages and len(self.browser_context.pages) > 0:
            try:
                await self.browser_context.pages[0].close()
            except Exception:
                pass

        self.initialized = True
        self._logger.debug("pool.initialized", pages=self.size)

    async def _add_page_to_pool(self) -> None:
        """Create a clean page and add it to the pool."""
        page = await self._create_clean_page()
        await self.available_pages.put(page)

    async def _create_clean_page(self) -> Page:
        """Create a new page with animations disabled.

        Returns:
            New Playwright page with CSS animations disabled
        """
        if self.browser_context is None:
            raise RuntimeError("browser_context is required")

        context: BrowserContext = self.browser_context
        page = await context.new_page()

        disable_animations = """
            *, *::before, *::after {
                animation-delay: 0s !important;
                animation-duration: 0s !important;
                transition-delay: 0s !important;
                transition-duration: 0s !important;
            }
        """
        await page.add_style_tag(content=disable_animations)
        return page

    async def get_page(self) -> Page:
        """Get a page from the pool.

        Wait for a page to become available if pool is exhausted.
        Automatically replaces closed pages.

        Returns:
            Playwright page from the pool

        Raises:
            RuntimeError: If pool not initialized
        """
        if not self.initialized:
            raise RuntimeError("Pool not initialized. Call initialize() first.")

        async with self._semaphore:
            page = await self.available_pages.get()

            if page.is_closed():
                self._logger.debug("pool.page_closed_replacing")
                page = await self._create_clean_page()

            self._logger.debug("pool.page_acquired")
            return page

    async def release_page(self, page: Page) -> None:
        """Return a page to the pool.

        If page is closed, creates a replacement.

        Args:
            page: Playwright page to return
        """
        if not self.initialized:
            return

        if page.is_closed():
            self._logger.debug("pool.page_released_closed", action="replacing")
            new_page = await self._create_clean_page()
            await self.available_pages.put(new_page)
        else:
            await self.available_pages.put(page)
            self._logger.debug("pool.page_released")

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[Page]:
        """Context manager for automatic page acquisition and release.

        Usage:
            async with pool.acquire() as page:
                await page.goto("https://example.com")

        Yields:
            Playwright page from the pool
        """
        page = await self.get_page()
        try:
            yield page
        finally:
            await self.release_page(page)

    async def close_all(self) -> None:
        """Close all pages in the pool."""
        self._logger.debug("pool.closing_all")

        while not self.available_pages.empty():
            page = await self.available_pages.get()
            if not page.is_closed():
                try:
                    await page.close()
                except Exception:
                    pass

        self.initialized = False
        self._logger.debug("pool.closed_all")

    @property
    def available_count(self) -> int:
        """Get number of available pages in the pool."""
        return self.available_pages.qsize()
