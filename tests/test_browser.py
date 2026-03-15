"""Tests for stealthkit.browser module."""

from pathlib import Path

import pytest

from stealthkit.browser import BrowserConfig


class TestBrowserConfig:
    """Tests for BrowserConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = BrowserConfig()
        assert config.headless is True
        assert config.user_data_dir is None
        assert config.user_agent is None
        assert config.viewport == {"width": 1920, "height": 1080}
        assert config.locale == "en-US"
        assert config.timezone == "America/Chicago"
        assert config.extensions == []
        assert config.disable_animations is True
        assert config.stealth_level == "standard"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = BrowserConfig(
            headless=False,
            user_agent="Custom Agent",
            viewport={"width": 1280, "height": 720},
            locale="en-GB",
            timezone="Europe/London",
            stealth_level="maximum",
        )
        assert config.headless is False
        assert config.user_agent == "Custom Agent"
        assert config.viewport == {"width": 1280, "height": 720}
        assert config.locale == "en-GB"
        assert config.timezone == "Europe/London"
        assert config.stealth_level == "maximum"

    def test_invalid_stealth_level(self):
        """Test that invalid stealth level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid stealth_level"):
            BrowserConfig(stealth_level="invalid")

    def test_invalid_viewport_width(self):
        """Test that invalid viewport width raises ValueError."""
        with pytest.raises(ValueError, match="viewport width"):
            BrowserConfig(viewport={"width": 100, "height": 720})

    def test_invalid_viewport_height(self):
        """Test that invalid viewport height raises ValueError."""
        with pytest.raises(ValueError, match="viewport height"):
            BrowserConfig(viewport={"width": 1920, "height": 100})

    def test_user_data_dir_path_conversion(self):
        """Test that user_data_dir is converted to Path."""
        config = BrowserConfig(user_data_dir="/tmp/test")
        assert isinstance(config.user_data_dir, Path)


class TestStealthBrowser:
    """Tests for StealthBrowser class."""

    def test_init_default_config(self):
        """Test StealthBrowser initialization with default config."""
        from stealthkit.browser import StealthBrowser

        browser = StealthBrowser()
        assert browser.config.headless is True
        assert browser.config.stealth_level == "standard"

    def test_init_custom_config(self):
        """Test StealthBrowser initialization with custom config."""
        from stealthkit.browser import StealthBrowser

        custom_config = BrowserConfig(
            headless=False,
            stealth_level="maximum",
        )
        browser = StealthBrowser(config=custom_config)
        assert browser.config.headless is False
        assert browser.config.stealth_level == "maximum"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test StealthBrowser as async context manager."""
        from stealthkit.browser import StealthBrowser

        async with StealthBrowser() as browser:
            assert browser.playwright is not None
            assert browser.context is not None
