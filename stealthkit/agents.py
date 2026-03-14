"""User agent generation for realistic browser fingerprints.

This module provides UserAgentGenerator for creating realistic user agents:
- Platform-specific user agents
- Random but valid version numbers
- Consistent with other browser properties

Usage:
    from stealthkit.agents import UserAgentGenerator

    generator = UserAgentGenerator()
    user_agent = generator.chrome()
    print(user_agent)
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class BrowserFingerprint:
    """Browser fingerprint configuration.

    Attributes:
        user_agent: User agent string
        platform: Browser platform
        locale: Browser locale
        timezone: Browser timezone
        viewport: Viewport dimensions
        device_scale_factor: Device scale factor
        is_mobile: Whether to simulate mobile
        has_touch: Whether to simulate touch
    """

    user_agent: str
    platform: str
    locale: str
    timezone: str
    viewport: dict[str, int]
    device_scale_factor: int
    is_mobile: bool
    has_touch: bool


class UserAgentGenerator:
    """Generate realistic user agent strings and browser fingerprints.

    Provides platform-specific user agents that match common browser versions.
    Can also generate complete fingerprints for browser context initialization.

    Usage:
        generator = UserAgentGenerator()

        # Just user agent
        ua = generator.chrome()

        # Complete fingerprint for context
        fingerprint = generator.fingerprint(platform="windows")
        await browser.new_context(**fingerprint.to_context_args())

    Attributes:
        chrome_versions: Available Chrome versions
        firefox_versions: Available Firefox versions
        safari_versions: Available Safari versions
    """

    CHROME_VERSIONS = [
        "120.0.0.0",
        "121.0.0.0",
        "122.0.0.0",
        "123.0.0.0",
        "124.0.0.0",
    ]

    FIREFOX_VERSIONS = [
        "120.0",
        "121.0",
        "122.0",
        "123.0",
        "124.0",
    ]

    SAFARI_VERSIONS = [
        "17.0",
        "17.1",
        "17.2",
        "17.3",
    ]

    def __init__(
        self,
        *,
        seed: int | None = None,
    ) -> None:
        """Initialize the user agent generator.

        Args:
            seed: Random seed for reproducible results (optional)
        """
        self._random = random.Random(seed)

    def chrome(
        self,
        platform: str = "windows",
    ) -> str:
        """Generate a Chrome user agent string.

        Args:
            platform: Platform - "windows", "macos", or "linux"

        Returns:
            Chrome user agent string
        """
        version = self._random.choice(self.CHROME_VERSIONS)

        if platform == "windows":
            return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        elif platform == "macos":
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        elif platform == "linux":
            return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        else:
            return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"

    def firefox(
        self,
        platform: str = "windows",
    ) -> str:
        """Generate a Firefox user agent string.

        Args:
            platform: Platform - "windows", "macos", or "linux"

        Returns:
            Firefox user agent string
        """
        version = self._random.choice(self.FIREFOX_VERSIONS)

        if platform == "windows":
            return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}"
        elif platform == "macos":
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{version}) Gecko/20100101 Firefox/{version}"
        elif platform == "linux":
            return f"Mozilla/5.0 (X11; Linux x86_64; rv:{version}) Gecko/20100101 Firefox/{version}"
        else:
            return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/20100101 Firefox/{version}"

    def safari(
        self,
        platform: str = "macos",
    ) -> str:
        """Generate a Safari user agent string.

        Args:
            platform: Platform - "macos" or "ios"

        Returns:
            Safari user agent string
        """
        version = self._random.choice(self.SAFARI_VERSIONS)

        if platform == "ios":
            return f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Mobile/15E148 Safari/604.1"
        else:
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"

    def random_platform(self) -> str:
        """Get a random platform.

        Returns:
            Random platform string
        """
        return self._random.choice(["windows", "macos", "linux"])

    def fingerprint(
        self,
        platform: str | None = None,
        browser: str = "chrome",
        locale: str = "en-US",
        timezone: str = "America/Chicago",
    ) -> BrowserFingerprint:
        """Generate a complete browser fingerprint.

        Args:
            platform: Platform - "windows", "macos", or "linux" (random if None)
            browser: Browser type - "chrome" or "firefox"
            locale: Browser locale
            timezone: Browser timezone

        Returns:
            BrowserFingerprint with all properties
        """
        if platform is None:
            platform = self.random_platform()

        if browser == "chrome":
            user_agent = self.chrome(platform)
        elif browser == "firefox":
            user_agent = self.firefox(platform)
        else:
            user_agent = self.chrome(platform)

        viewport_width = self._random.randint(1200, 1920)
        viewport_height = self._random.randint(800, 1080)

        return BrowserFingerprint(
            user_agent=user_agent,
            platform=platform,
            locale=locale,
            timezone=timezone,
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
        )


def get_platform_from_user_agent(user_agent: str) -> str:
    """Extract platform from user agent string.

    Args:
        user_agent: User agent string

    Returns:
        Platform string - "windows", "macos", "linux", "ios", "android", or "unknown"
    """
    if "Windows" in user_agent:
        return "windows"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        return "ios"
    elif "Android" in user_agent:
        return "android"
    elif "Macintosh" in user_agent or "Mac OS X" in user_agent:
        return "macos"
    elif "Linux" in user_agent or "X11" in user_agent:
        return "linux"
    else:
        return "unknown"
