"""Tests for stealthkit.stealth module."""

import pytest

from stealthkit.stealth import STEALTH_LEVELS, apply_stealth


class TestApplyStealth:
    """Tests for apply_stealth function."""

    def test_stealth_levels_defined(self):
        """Test that all stealth levels are defined."""
        assert "basic" in STEALTH_LEVELS
        assert "standard" in STEALTH_LEVELS
        assert "maximum" in STEALTH_LEVELS

    def test_basic_script_content(self):
        """Test basic script contains essential patches."""
        script = STEALTH_LEVELS["basic"]
        assert "navigator.webdriver" in script
        assert "window.chrome" in script
        assert "navigator.languages" in script

    def test_standard_script_content(self):
        """Test standard script contains all basic patches plus more."""
        script = STEALTH_LEVELS["standard"]
        assert "navigator.webdriver" in script
        assert "permissions.query" in script
        assert "getBattery" in script

    def test_maximum_script_content(self):
        """Test maximum script contains all patches."""
        script = STEALTH_LEVELS["maximum"]
        assert "navigator.webdriver" in script
        assert "permissions.query" in script
        assert "'plugins'" in script or "plugins" in script
        assert "PlatformOs" in script

    @pytest.mark.asyncio
    async def test_apply_stealth_invalid_level(self):
        """Test that invalid level raises ValueError."""
        from unittest.mock import AsyncMock

        page = AsyncMock()

        with pytest.raises(ValueError, match="Invalid stealth level"):
            await apply_stealth(page, level="invalid")

    @pytest.mark.asyncio
    async def test_apply_stealth_basic(self):
        """Test apply_stealth with basic level."""
        from unittest.mock import AsyncMock

        page = AsyncMock()

        await apply_stealth(page, level="basic")

        page.add_init_script.assert_called_once()
        script_arg = page.add_init_script.call_args[0][0]
        assert "navigator.webdriver" in script_arg

    @pytest.mark.asyncio
    async def test_apply_stealth_standard(self):
        """Test apply_stealth with standard level."""
        from unittest.mock import AsyncMock

        page = AsyncMock()

        await apply_stealth(page, level="standard")

        page.add_init_script.assert_called_once()
        script_arg = page.add_init_script.call_args[0][0]
        assert "navigator.webdriver" in script_arg
        assert "permissions.query" in script_arg


class TestStealthIntegration:
    """Integration tests with real browser."""

    @pytest.mark.asyncio
    async def test_apply_stealth_to_page(self):
        """Test applying stealth to a real page."""
        from stealthkit.browser import StealthBrowser

        async with StealthBrowser() as browser:
            page = await browser.new_page()

            webdriver_value = await page.evaluate("navigator.webdriver")
            assert webdriver_value is None or webdriver_value is False

            await page.close()
