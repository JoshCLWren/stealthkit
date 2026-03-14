"""Tests for stealthkit.agents module."""


from stealthkit.agents import (
    BrowserFingerprint,
    UserAgentGenerator,
    get_platform_from_user_agent,
)


class TestUserAgentGenerator:
    """Tests for UserAgentGenerator class."""

    def test_init_default(self):
        """Test default initialization."""
        gen = UserAgentGenerator()
        assert gen._random is not None

    def test_init_with_seed(self):
        """Test initialization with seed for reproducibility."""
        gen1 = UserAgentGenerator(seed=42)
        gen2 = UserAgentGenerator(seed=42)

        assert gen1.chrome() == gen2.chrome()

    def test_chrome_windows(self):
        """Test Chrome user agent for Windows."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.chrome(platform="windows")

        assert "Windows NT 10.0" in ua
        assert "Chrome/" in ua
        assert "Safari" in ua

    def test_chrome_macos(self):
        """Test Chrome user agent for macOS."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.chrome(platform="macos")

        assert "Macintosh" in ua
        assert "Chrome/" in ua

    def test_chrome_linux(self):
        """Test Chrome user agent for Linux."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.chrome(platform="linux")

        assert "Linux" in ua or "X11" in ua
        assert "Chrome/" in ua

    def test_firefox_windows(self):
        """Test Firefox user agent for Windows."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.firefox(platform="windows")

        assert "Windows" in ua
        assert "Firefox/" in ua
        assert "Gecko" in ua

    def test_firefox_macos(self):
        """Test Firefox user agent for macOS."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.firefox(platform="macos")

        assert "Macintosh" in ua or "Mac OS X" in ua
        assert "Firefox/" in ua

    def test_firefox_linux(self):
        """Test Firefox user agent for Linux."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.firefox(platform="linux")

        assert "Linux" in ua or "X11" in ua
        assert "Firefox/" in ua

    def test_safari_macos(self):
        """Test Safari user agent for macOS."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.safari(platform="macos")

        assert "Macintosh" in ua or "Mac OS X" in ua
        assert "Safari" in ua

    def test_safari_ios(self):
        """Test Safari user agent for iOS."""
        gen = UserAgentGenerator(seed=123)

        ua = gen.safari(platform="ios")

        assert "iPhone" in ua
        assert "Safari" in ua

    def test_random_platform(self):
        """Test random platform selection."""
        gen = UserAgentGenerator(seed=42)

        platforms = {gen.random_platform() for _ in range(100)}

        assert len(platforms) >= 1

    def test_fingerprint_default(self):
        """Test fingerprint generation with defaults."""
        gen = UserAgentGenerator(seed=123)

        fp = gen.fingerprint()

        assert isinstance(fp, BrowserFingerprint)
        assert fp.user_agent
        assert fp.platform in ("windows", "macos", "linux")
        assert fp.locale == "en-US"
        assert fp.timezone == "America/Chicago"
        assert "width" in fp.viewport
        assert "height" in fp.viewport

    def test_fingerprint_custom(self):
        """Test fingerprint generation with custom options."""
        gen = UserAgentGenerator(seed=123)

        fp = gen.fingerprint(
            platform="windows",
            browser="chrome",
            locale="en-GB",
            timezone="Europe/London",
        )

        assert fp.platform == "windows"
        assert "Windows" in fp.user_agent
        assert fp.locale == "en-GB"
        assert fp.timezone == "Europe/London"

    def test_fingerprint_firefox(self):
        """Test fingerprint for Firefox browser."""
        gen = UserAgentGenerator(seed=123)

        fp = gen.fingerprint(browser="firefox")

        assert "Firefox" in fp.user_agent


class TestBrowserFingerprint:
    """Tests for BrowserFingerprint dataclass."""

    def test_fingerprint_creation(self):
        """Test creating a fingerprint."""
        fp = BrowserFingerprint(
            user_agent="Test Agent",
            platform="windows",
            locale="en-US",
            timezone="America/Chicago",
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
        )

        assert fp.user_agent == "Test Agent"
        assert fp.platform == "windows"
        assert fp.viewport["width"] == 1920


class TestGetPlatformFromUserAgent:
    """Tests for get_platform_from_user_agent function."""

    def test_windows_detection(self):
        """Test Windows platform detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        assert get_platform_from_user_agent(ua) == "windows"

    def test_macos_detection(self):
        """Test macOS platform detection."""
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36"
        assert get_platform_from_user_agent(ua) == "macos"

    def test_linux_detection(self):
        """Test Linux platform detection."""
        ua = "Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0"
        assert get_platform_from_user_agent(ua) == "linux"

    def test_ios_detection(self):
        """Test iOS platform detection."""
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile"
        assert get_platform_from_user_agent(ua) == "ios"

    def test_android_detection(self):
        """Test Android platform detection."""
        ua = "Mozilla/5.0 (Linux; Android 14) Chrome/120.0"
        assert get_platform_from_user_agent(ua) == "android"

    def test_unknown_detection(self):
        """Test unknown platform detection."""
        ua = "Mozilla/5.0 (Unknown)"
        assert get_platform_from_user_agent(ua) == "unknown"
