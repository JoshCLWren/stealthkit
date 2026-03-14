"""Stealth patches for anti-detection in Playwright.

This module provides JS injection patches to make automated browsers
appear more like real browsers to detection systems.

Features:
- Override navigator.webdriver
- Mock window.chrome object
- Fix permissions API
- Add realistic plugins
- Set hardware properties

Usage:
    from stealthkit.stealth import apply_stealth

    async with StealthBrowser() as browser:
        page = await browser.new_page()
        await apply_stealth(page, level="standard")
        await page.goto("https://example.com")
"""

from __future__ import annotations

from typing import Any

import structlog
from playwright_stealth import Stealth

logger = structlog.get_logger(__name__)


BASIC_STEALTH_SCRIPT = """
// Override navigator.webdriver
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Mock window.chrome
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};

// Override navigator.languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Fix hardware properties
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8
});

Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8
});
"""

STANDARD_STEALTH_SCRIPT = (
    BASIC_STEALTH_SCRIPT
    + """
// Fix permission API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// Set realistic window properties
Object.defineProperty(window, 'devicePixelRatio', {
    get: () => 1
});

// Add battery API mock
if (!navigator.getBattery) {
    navigator.getBattery = () => {
        return Promise.resolve({
            charging: true,
            chargingTime: 0,
            dischargingTime: Infinity,
            level: 1.0
        });
    };
}

// Fix language
Object.defineProperty(navigator, 'language', {
    get: () => 'en-US'
});

// Fix platform
Object.defineProperty(navigator, 'platform', {
    get: () => 'Win32'
});
"""
)

MAXIMUM_STEALTH_SCRIPT = (
    STANDARD_STEALTH_SCRIPT
    + """
// Add plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        return [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf"},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf"},
                description: "Portable Document Format",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            },
            {
                0: {type: "application/x-nacl", suffixes: ""},
                1: {type: "application/x-pnacl", suffixes: ""},
                description: "Native Client Executable",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client"
            }
        ];
    }
});

// Full chrome runtime mock
window.chrome = {
    runtime: {
        PlatformOs: {
            MAC: 'mac',
            WIN: 'win',
            ANDROID: 'android',
            CROS: 'cros',
            LINUX: 'linux',
            OPENBSD: 'openbsd'
        },
        PlatformArch: {
            ARM: 'arm',
            X86_32: 'x86-32',
            X86_64: 'x86-64'
        },
        PlatformNaclArch: {
            ARM: 'arm',
            X86_32: 'x86-32',
            X86_64: 'x86-64'
        },
        RequestUpdateCheckStatus: {
            THROTTLED: 'throttled',
            NO_UPDATE: 'no_update',
            UPDATE_AVAILABLE: 'update_available'
        },
        OnInstalledReason: {
            INSTALL: 'install',
            UPDATE: 'update',
            CHROME_UPDATE: 'chrome_update',
            SHARED_MODULE_UPDATE: 'shared_module_update'
        },
        OnRestartRequiredReason: {
            APP_UPDATE: 'app_update',
            OS_UPDATE: 'os_update',
            PERIODIC: 'periodic'
        }
    },
    loadTimes: function() {
        return {
            requestTime: Date.now() / 1000,
            startLoadTime: Date.now() / 1000,
            commitLoadTime: Date.now() / 1000,
            finishDocumentLoadTime: Date.now() / 1000,
            finishLoadTime: Date.now() / 1000,
            firstPaintTime: Date.now() / 1000,
            firstPaintAfterLoadTime: Date.now() / 1000,
            navigationType: 'Other',
            wasFetchedViaSpdy: false,
            wasNpnNegotiated: true,
            npnNegotiatedProtocol: 'h2',
            wasAlternateProtocolAvailable: false,
            connectionInfo: 'h2'
        };
    },
    csi: function() {
        return {
            onloadT: Date.now(),
            pageT: Date.now() - Math.random() * 1000,
            startE: Date.now() - Math.random() * 2000,
            tran: 15
        };
    },
    app: {
        isInstalled: false,
        InstallState: {
            DISABLED: 'disabled',
            INSTALLED: 'installed',
            NOT_INSTALLED: 'not_installed'
        },
        RunningState: {
            CANNOT_RUN: 'cannot_run',
            READY_TO_RUN: 'ready_to_run',
            RUNNING: 'running'
        }
    }
};
"""
)

STEALTH_LEVELS = {
    "basic": BASIC_STEALTH_SCRIPT,
    "standard": STANDARD_STEALTH_SCRIPT,
    "maximum": MAXIMUM_STEALTH_SCRIPT,
}


async def apply_stealth(page: Any, level: str = "standard") -> None:
    """Apply stealth patches to a Playwright page.

    Uses playwright-stealth library for core patches plus additional
    custom JS injections based on stealth level.

    Args:
        page: Playwright page to patch
        level: Stealth level - "basic", "standard", or "maximum"
            - basic: Minimal patches (webdriver override, languages, hardware)
            - standard: Medium patches (+ permissions, battery, platform)
            - maximum: Full patches (+ plugins, chrome runtime mock)

    Raises:
        ValueError: If level is not valid
    """
    if level not in STEALTH_LEVELS:
        raise ValueError(
            f"Invalid stealth level: {level}. Must be one of: {list(STEALTH_LEVELS.keys())}"
        )

    logger.debug("stealth.applying", level=level)

    try:
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
    except Exception as e:
        logger.warning("stealth.library_failed", error=str(e))

    script = STEALTH_LEVELS[level]
    await page.add_init_script(script)

    logger.debug("stealth.applied", level=level)
