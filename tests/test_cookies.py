"""Tests for stealthkit.cookies module."""

import json

import pytest

from stealthkit.cookies import (
    clear_cookies,
    get_cookie_names,
    get_cookie_value,
    has_cookie,
    load_cookies,
    save_cookies,
)


class TestSaveLoadCookies:
    """Tests for save_cookies and load_cookies functions."""

    @pytest.mark.asyncio
    async def test_save_and_load_cookies(self, tmp_path):
        """Test saving and loading cookies to/from file."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.cookies = AsyncMock(
            return_value=[
                {"name": "session", "value": "abc123", "domain": ".example.com"},
                {"name": "user", "value": "john", "domain": ".example.com"},
            ]
        )

        cookie_file = tmp_path / "cookies.json"

        await save_cookies(context, cookie_file)

        assert cookie_file.exists()

        with open(cookie_file) as f:
            saved = json.load(f)
        assert len(saved) == 2
        assert saved[0]["name"] == "session"

        context2 = AsyncMock()
        context2.add_cookies = AsyncMock()

        result = await load_cookies(context2, cookie_file)

        assert result is True
        context2.add_cookies.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_cookies_file_not_found(self, tmp_path):
        """Test loading cookies when file doesn't exist."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.add_cookies = AsyncMock()

        result = await load_cookies(context, tmp_path / "nonexistent.json")

        assert result is False
        context.add_cookies.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_cookies_creates_parent_dirs(self, tmp_path):
        """Test that save_cookies creates parent directories."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.cookies = AsyncMock(return_value=[{"name": "test", "value": "val"}])

        cookie_file = tmp_path / "subdir" / "cookies.json"

        await save_cookies(context, cookie_file)

        assert cookie_file.parent.exists()
        assert cookie_file.exists()


class TestClearCookies:
    """Tests for clear_cookies function."""

    @pytest.mark.asyncio
    async def test_clear_cookies(self):
        """Test clearing all cookies."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.clear_cookies = AsyncMock()

        await clear_cookies(context)

        context.clear_cookies.assert_called_once()


class TestCookieHelpers:
    """Tests for cookie helper functions."""

    @pytest.mark.asyncio
    async def test_get_cookie_names(self):
        """Test getting cookie names."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.cookies = AsyncMock(
            return_value=[
                {"name": "session", "value": "abc"},
                {"name": "user", "value": "john"},
            ]
        )

        names = await get_cookie_names(context)

        assert "session" in names
        assert "user" in names

    @pytest.mark.asyncio
    async def test_has_cookie_found(self):
        """Test checking for existing cookie."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.cookies = AsyncMock(
            return_value=[
                {"name": "session", "value": "abc", "domain": ".example.com"},
            ]
        )

        result = await has_cookie(context, "session")
        assert result is True

        result = await has_cookie(context, "session", domain=".example.com")
        assert result is True

    @pytest.mark.asyncio
    async def test_has_cookie_not_found(self):
        """Test checking for non-existing cookie."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.cookies = AsyncMock(
            return_value=[
                {"name": "session", "value": "abc"},
            ]
        )

        result = await has_cookie(context, "nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_cookie_value(self):
        """Test getting cookie value."""
        from unittest.mock import AsyncMock

        context = AsyncMock()
        context.cookies = AsyncMock(
            return_value=[
                {"name": "session", "value": "abc123", "domain": ".example.com"},
            ]
        )

        value = await get_cookie_value(context, "session")
        assert value == "abc123"

        value = await get_cookie_value(context, "nonexistent")
        assert value is None
