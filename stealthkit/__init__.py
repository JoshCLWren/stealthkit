"""Stealthkit — Playwright stealth automation.

Provides:
- StealthBrowser: Context manager for anti-detection browser automation
- PagePool: Semaphore-backed async page management
- Stealth patches: JS injection patches for anti-detection
- Human behavior simulation: Delays, mouse movements, scrolling
- Cookie persistence: Save/load cookies to JSON
- User agent generation: Realistic user agent strings
- Rate limiting: Exponential backoff for request throttling
"""

__version__ = "0.1.0"

from stealthkit.agents import UserAgentGenerator
from stealthkit.browser import BrowserConfig, StealthBrowser
from stealthkit.cookies import load_cookies, save_cookies
from stealthkit.human import human_like_delay, navigate_with_human_behavior, random_mouse_movements
from stealthkit.pool import PagePool
from stealthkit.ratelimit import RateLimiter
from stealthkit.stealth import apply_stealth

__all__ = [
    "StealthBrowser",
    "BrowserConfig",
    "PagePool",
    "apply_stealth",
    "human_like_delay",
    "random_mouse_movements",
    "navigate_with_human_behavior",
    "save_cookies",
    "load_cookies",
    "UserAgentGenerator",
    "RateLimiter",
]
