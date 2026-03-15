"""Human behavior simulation for anti-detection.

This module provides functions to simulate human-like behavior:
- Randomized delays between actions
- Human-like mouse movements
- Natural scrolling patterns

Usage:
    from stealthkit.human import human_like_delay, navigate_with_human_behavior

    async with pool.acquire() as page:
        await navigate_with_human_behavior(page, "https://example.com")
        await human_like_delay(min_seconds=1.0, max_seconds=3.0)
"""

from __future__ import annotations

import asyncio
import random
from typing import Literal

import structlog
from playwright.async_api import Page

logger = structlog.get_logger(__name__)


async def human_like_delay(
    min_seconds: float = 0.5,
    max_seconds: float = 2.0,
) -> None:
    """Sleep for a random duration to simulate human typing/thinking.

    Uses a weighted random distribution that favors shorter delays
    with occasional longer pauses.

    Args:
        min_seconds: Minimum delay (default: 0.5)
        max_seconds: Maximum delay (default: 2.0)
    """
    delay = min_seconds + random.random() * (max_seconds - min_seconds)

    if random.random() < 0.1:
        delay += random.uniform(1.0, 3.0)

    logger.debug("human.delay", seconds=delay)
    await asyncio.sleep(delay)


async def random_mouse_movements(
    page: Page,
    count: int = 3,
) -> None:
    """Perform random mouse movements on the page.

    Simulates natural mouse behavior to avoid detection as a bot.
    Movements are distributed across the viewport.

    Args:
        page: Playwright page
        count: Number of movements to perform (default: 3)
    """
    viewport = page.viewport_size or {"width": 1920, "height": 1080}
    width = viewport.get("width", 1920)
    height = viewport.get("height", 1080)

    for _ in range(count):
        x = random.randint(100, width - 100)
        y = random.randint(100, height - 100)

        await page.mouse.move(x, y)
        await human_like_delay(0.05, 0.15)

    logger.debug("human.mouse_movements", count=count)


async def human_scroll(
    page: Page,
    distance: int = 1000,
) -> None:
    """Perform a human-like scroll down the page.

    Uses wheel events with variable speed and pauses.

    Args:
        page: Playwright page
        distance: Total distance to scroll in pixels (default: 1000)
    """
    remaining = distance
    scroll_step = min(distance // 5, 500)

    while remaining > 0:
        step = min(scroll_step + random.randint(-50, 50), remaining)
        step = max(step, 50)

        await page.mouse.wheel(0, step)
        remaining -= step

        await human_like_delay(0.1, 0.3)

    logger.debug("human.scroll", distance=distance)


async def navigate_with_human_behavior(
    page: Page,
    url: str,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "domcontentloaded",
    timeout: float = 30000,
) -> None:
    """Navigate to a URL with human-like behavior.

    This function:
    1. Applies a small pre-navigation delay
    2. Navigates to the URL
    3. Waits for the page to load
    4. Performs random mouse movements
    5. Applies a post-navigation delay

    Args:
        page: Playwright page
        url: URL to navigate to
        wait_until: Wait condition - "load", "domcontentloaded", etc.
        timeout: Navigation timeout in milliseconds (default: 30000)
    """
    logger.debug("human.navigate_start", url=url)

    await human_like_delay(0.3, 1.0)

    await page.goto(url, wait_until=wait_until, timeout=timeout)

    await random_mouse_movements(page, count=2)

    logger.debug("human.navigate_end", url=url)


async def type_like_human(
    page: Page,
    selector: str,
    text: str,
    *,
    min_delay: float = 0.05,
    max_delay: float = 0.15,
    mistake_probability: float = 0.02,
) -> None:
    """Type text with human-like delays and occasional mistakes.

    Simulates:
    - Variable typing speed
    - Occasional typos (with corrections)
    - Natural pauses between words

    Args:
        page: Playwright page
        selector: CSS selector for input field
        text: Text to type
        min_delay: Minimum delay between keystrokes
        max_delay: Maximum delay between keystrokes
        mistake_probability: Chance of making a typo (0-1)
    """
    await page.click(selector)
    await human_like_delay(0.2, 0.5)

    for char in text:
        if char == " ":
            await human_like_delay(0.1, 0.3)

        if random.random() < mistake_probability:
            wrong_char = chr(ord(char) + random.choice([-1, 1]))
            await page.keyboard.press(wrong_char)
            await human_like_delay(0.1, 0.3)
            await page.keyboard.press("Backspace")
            await human_like_delay(0.1, 0.2)

        await page.keyboard.press(char)
        await asyncio.sleep(min_delay + random.random() * (max_delay - min_delay))

    logger.debug("human.type_end", text_length=len(text))


async def scroll_to_element(
    page: Page,
    selector: str,
) -> None:
    """Scroll an element into view with human-like behavior.

    Args:
        page: Playwright page
        selector: CSS selector for the element
    """
    element = await page.query_selector(selector)
    if not element:
        return

    await element.scroll_into_view_if_needed()
    await random_mouse_movements(page, count=1)

    logger.debug("human.scroll_to_element", selector=selector)
