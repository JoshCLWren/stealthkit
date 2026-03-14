"""Cookie persistence for browser sessions.

This module provides functions to save and load browser cookies:
- Save cookies to JSON file
- Load cookies from JSON file
- Automatic path creation

Usage:
    from stealthkit.cookies import save_cookies, load_cookies

    async with StealthBrowser() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com/login")
        # ... login ...
        await save_cookies(page.context, "cookies.json")

    # Later:
    async with StealthBrowser() as browser:
        page = await browser.new_page()
        await load_cookies(page.context, "cookies.json")
        await page.goto("https://example.com")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


async def save_cookies(
    context: Any,
    path: str | Path,
) -> None:
    """Save browser cookies to a JSON file.

    Args:
        context: Playwright browser context
        path: Path to save cookies file
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cookies = await context.cookies()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)

    logger.debug("cookies.saved", path=str(path), count=len(cookies))


async def load_cookies(
    context: Any,
    path: str | Path,
) -> bool:
    """Load browser cookies from a JSON file.

    Args:
        context: Playwright browser context
        path: Path to cookies file

    Returns:
        True if cookies were loaded, False if file doesn't exist
    """
    path = Path(path)

    if not path.exists():
        logger.debug("cookies.file_not_found", path=str(path))
        return False

    with open(path, encoding="utf-8") as f:
        cookies = json.load(f)

    await context.add_cookies(cookies)

    logger.debug("cookies.loaded", path=str(path), count=len(cookies))
    return True


async def clear_cookies(
    context: Any,
) -> None:
    """Clear all cookies from the browser context.

    Args:
        context: Playwright browser context
    """
    await context.clear_cookies()
    logger.debug("cookies.cleared")


async def get_cookie_names(
    context: Any,
) -> list[str]:
    """Get names of all cookies in the context.

    Args:
        context: Playwright browser context

    Returns:
        List of cookie names
    """
    cookies = await context.cookies()
    return [cookie.get("name", "") for cookie in cookies]


async def has_cookie(
    context: Any,
    name: str,
    domain: str | None = None,
) -> bool:
    """Check if a specific cookie exists.

    Args:
        context: Playwright browser context
        name: Cookie name to check
        domain: Optional domain to match

    Returns:
        True if cookie exists
    """
    cookies = await context.cookies()

    for cookie in cookies:
        if cookie.get("name") == name:
            if domain is None or cookie.get("domain") == domain:
                return True

    return False


async def get_cookie_value(
    context: Any,
    name: str,
    domain: str | None = None,
) -> str | None:
    """Get the value of a specific cookie.

    Args:
        context: Playwright browser context
        name: Cookie name
        domain: Optional domain to match

    Returns:
        Cookie value or None if not found
    """
    cookies = await context.cookies()

    for cookie in cookies:
        if cookie.get("name") == name:
            if domain is None or cookie.get("domain") == domain:
                return cookie.get("value")

    return None
