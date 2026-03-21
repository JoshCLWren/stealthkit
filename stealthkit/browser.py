"""Browser context management with anti-detection features.

This module provides StealthBrowser, an async context manager that handles:
- Browser lifecycle (launch/close)
- Anti-detection settings
- Persistent context with user data
- Extension loading (uBlock, etc.)

Usage:
    async with StealthBrowser() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        content = await page.content()
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Any

import structlog
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = structlog.get_logger(__name__)


@dataclass
class BrowserConfig:
    """Configuration for StealthBrowser.

    Attributes:
        headless: Run in headless mode (default: True)
        user_data_dir: Directory for persistent browser data (default: ./user_data)
        user_agent: Custom user agent string
        viewport: Viewport dimensions (default: 1920x1080)
        locale: Browser locale (default: en-US)
        timezone: Browser timezone (default: America/Chicago)
        extensions: List of extension paths to load
        disable_animations: Disable CSS animations (default: True)
        stealth_level: Stealth preset - "basic", "standard", or "maximum" (default: "standard")
    """

    headless: bool = True
    user_data_dir: str | Path | None = None
    user_agent: str | None = None
    viewport: dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    locale: str = "en-US"
    timezone: str = "America/Chicago"
    extensions: list[str | Path] = field(default_factory=list)
    disable_animations: bool = True
    stealth_level: str = "standard"

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.stealth_level not in ("basic", "standard", "maximum"):
            raise ValueError(
                f"Invalid stealth_level: {self.stealth_level}. Must be 'basic', 'standard', or 'maximum'"
            )

        if self.viewport.get("width", 0) < 320:
            raise ValueError("viewport width must be at least 320")
        if self.viewport.get("height", 0) < 240:
            raise ValueError("viewport height must be at least 240")

        if self.user_data_dir is not None:
            self.user_data_dir = Path(self.user_data_dir)


class StealthBrowser:
    """Async context manager for Playwright browser with stealth patches.

    This class provides a simple interface for creating and managing a
    Playwright browser instance with anti-detection features pre-applied.

    Features:
    - Automatic anti-detection JS injection
    - Persistent browser context with user data
    - Optional uBlock extension loading
    - Configurable stealth levels
    - Clean resource cleanup

    Usage:
        async with StealthBrowser() as browser:
            page = await browser.new_page()
            await page.goto("https://example.com")

        # Or with custom config:
        config = BrowserConfig(headless=False, stealth_level="maximum")
        async with StealthBrowser(config) as browser:
            ...

    Attributes:
        config: Browser configuration
        playwright: Playwright instance
        browser: Browser instance
        context: Browser context
    """

    def __init__(
        self,
        config: BrowserConfig | None = None,
    ) -> None:
        """Initialize StealthBrowser.

        Args:
            config: Browser configuration (uses defaults if not provided)
        """
        self.config = config or BrowserConfig()
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self._logger = structlog.get_logger(__name__).bind(
            headless=self.config.headless,
            stealth_level=self.config.stealth_level,
        )

    async def __aenter__(self) -> StealthBrowser:
        """Enter async context and initialize browser."""
        await self._launch()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context and cleanup resources."""
        await self._close()

    async def _launch(self) -> None:
        """Launch the browser with configured settings."""
        self.playwright = await async_playwright().start()

        args = self._get_browser_args()
        launch_options = {
            "headless": self.config.headless,
            "args": args,
        }

        user_data_dir = self._get_user_data_dir()
        if user_data_dir:
            user_data_dir.mkdir(parents=True, exist_ok=True)

        self._logger.debug(
            "browser.launching",
            headless=self.config.headless,
            user_data=str(user_data_dir) if user_data_dir else None,
        )

        if user_data_dir:
            launch_opts = dict(launch_options)
            if self.config.user_agent:
                launch_opts["user_agent"] = self.config.user_agent
            self.context = await self.playwright.chromium.launch_persistent_context(
                str(user_data_dir),
                **launch_opts,
                viewport=self.config.viewport,  # type: ignore[arg-type]
                locale=self.config.locale,
                timezone_id=self.config.timezone,
                ignore_https_errors=True,
            )
        else:
            self.browser = await self.playwright.chromium.launch(**launch_options)
            self.context = await self.browser.new_context(
                viewport=self.config.viewport,  # type: ignore[arg-type]
                locale=self.config.locale,
                timezone_id=self.config.timezone,
                user_agent=self.config.user_agent,
                ignore_https_errors=True,
            )

        self.context.on("page", lambda page: self._apply_stealth_to_page(page))

        self._logger.debug("browser.launched")

    async def _close(self) -> None:
        """Close the browser and cleanup resources."""
        if self.context:
            await self.context.close()
            self.context = None
            self._logger.debug("browser.context_closed")

        if self.browser:
            await self.browser.close()
            self.browser = None
            self._logger.debug("browser.closed")

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            self._logger.debug("playwright.stopped")

    async def _apply_stealth_to_page(self, page: Page) -> None:
        """Apply stealth patches to a page.

        Args:
            page: Playwright page to patch
        """
        from stealthkit.stealth import apply_stealth

        await apply_stealth(page, level=self.config.stealth_level)

        if self.config.disable_animations:
            await page.add_style_tag(content=self._get_animation_css())

    def _get_browser_args(self) -> list[str]:
        """Get Chrome command line arguments based on config."""
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--no-first-run",
            "--no-default-browser-check",
            "--force-color-profile=srgb",
        ]

        for ext_path in self.config.extensions:
            path = Path(ext_path)
            if path.exists():
                args.extend(
                    [
                        f"--disable-extensions-except={path}",
                        f"--load-extension={path}",
                    ]
                )

        return args

    def _get_user_data_dir(self) -> Path | None:
        """Get user data directory path."""
        if self.config.user_data_dir:
            return Path(self.config.user_data_dir)

        env_dir = os.environ.get("STEALTHKIT_USER_DATA_DIR")
        if env_dir:
            return Path(env_dir)

        return None

    def _get_animation_css(self) -> str:
        """Get CSS to disable animations."""
        return """
            *, *::before, *::after {
                animation-delay: 0s !important;
                animation-duration: 0s !important;
                transition-delay: 0s !important;
                transition-duration: 0s !important;
            }
        """

    async def new_page(self) -> Any:
        """Create a new page with stealth patches applied.

        Returns:
            Playwright page with anti-detection features

        Raises:
            RuntimeError: If browser/context not initialized
        """
        if not self.context:
            raise RuntimeError("Browser not initialized. Use 'async with' context.")

        page = await self.context.new_page()
        await self._apply_stealth_to_page(page)
        return page

    @asynccontextmanager
    async def page(self) -> AsyncIterator[Page]:
        """Context manager for getting a page that auto-closes.

        Usage:
            async with browser.page() as page:
                await page.goto("https://example.com")

        Yields:
            Playwright page with anti-detection features
        """
        page = await self.new_page()
        try:
            yield page
        finally:
            await page.close()
