# stealthkit

[![CI Status](https://github.com/JoshCLWren/stealthkit/workflows/CI/badge.svg)](https://github.com/JoshCLWren/stealthkit/actions)

Playwright stealth automation for anti-detection browser automation.

## Overview

stealthkit provides a comprehensive suite of tools for browser automation that evades detection systems. Built on Playwright with stealth patches, human behavior simulation, and efficient resource management.

## Features

- **StealthBrowser**: Async context manager for anti-detection browser automation
- **PagePool**: Semaphore-backed async page pool for concurrent scraping
- **Stealth Patches**: JavaScript injection patches for anti-detection
- **Human Behavior Simulation**: Delays, mouse movements, and scrolling
- **Cookie Persistence**: Save/load cookies to JSON
- **User Agent Generation**: Realistic user agent strings
- **Rate Limiting**: Exponential backoff for request throttling

## Tech Stack

- **Python 3.13+** with type hints throughout
- **Playwright**: Browser automation
- **playwright-stealth**: Anti-detection patches
- **structlog**: Structured logging

## Installation

```bash
# Clone the repository
git clone https://github.com/JoshCLWren/stealthkit.git
cd stealthkit

# Install dependencies
uv sync --all-extras

# Install Playwright browsers
playwright install chromium
```

## Quick Start

```python
import asyncio
from stealthkit import StealthBrowser, BrowserConfig

async def main():
    # Basic usage with default configuration
    async with StealthBrowser() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        content = await page.content()
        print(content)

    # With custom configuration
    config = BrowserConfig(
        headless=False,
        stealth_level="maximum",
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone="America/Chicago"
    )
    async with StealthBrowser(config) as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage Examples

### Page Pool for Concurrent Scraping

```python
from stealthkit import StealthBrowser, PagePool

async def scrape_with_pool(urls: list[str]):
    async with StealthBrowser() as browser:
        pool = PagePool(size=5, browser_context=browser.context)
        await pool.initialize()

        async with pool.acquire() as page:
            await page.goto(urls[0])
            content = await page.content()
```

### Human Behavior Simulation

```python
from stealthkit import StealthBrowser, navigate_with_human_behavior

async def human_like_scraping(url: str):
    async with StealthBrowser() as browser:
        page = await browser.new_page()
        await navigate_with_human_behavior(page, url)
        # Automatically adds delays, mouse movements, and scrolling
```

### Cookie Persistence

```python
from stealthkit import StealthBrowser, save_cookies, load_cookies

async def scrape_with_cookies():
    async with StealthBrowser() as browser:
        page = await browser.new_page()
        
        # Load existing cookies
        await load_cookies(page, "cookies.json")
        
        await page.goto("https://example.com")
        
        # Save cookies for next session
        await save_cookies(page, "cookies.json")
```

### Rate Limiting

```python
from stealthkit import RateLimiter

# Rate limiter with exponential backoff
limiter = RateLimiter(max_requests=10, window_seconds=60)

async def make_request():
    await limiter.acquire()
    # Make your request here
```

## Development Workflow

### First Time Setup

```bash
# Install dependencies
uv sync --all-extras

# Install Playwright browsers
playwright install chromium

# Activate the virtual environment (do this once per session)
source .venv/bin/activate
```

### Daily Development

```bash
# Run tests
pytest

# Run tests with coverage report
pytest --cov-report=term-missing

# Run linting
make lint

# Format code with ruff
ruff format .
```

### Make Commands

- `make lint` - Run all linting checks (ruff + pyright)
- `make pytest` - Run the test suite
- `make venv` - Create virtual environment
- `make sync` - Install/update dependencies

## Project Structure

```
stealthkit/
├── stealthkit/           # Main package
│   ├── __init__.py      # Package exports
│   ├── browser.py       # StealthBrowser and BrowserConfig
│   ├── pool.py          # PagePool for concurrent scraping
│   ├── stealth.py       # Anti-detection patches
│   ├── human.py         # Human behavior simulation
│   ├── cookies.py       # Cookie persistence
│   ├── agents.py        # User agent generation
│   └── ratelimit.py     # Rate limiting
├── tests/               # Test suite
│   ├── conftest.py      # pytest fixtures
│   └── test_*.py        # Module tests
├── scripts/
│   └── lint.sh         # Linting script
├── pyproject.toml      # Project configuration
└── uv.lock             # Dependency lockfile
```

## Configuration

### BrowserConfig Options

```python
from stealthkit import BrowserConfig

config = BrowserConfig(
    headless=True,                    # Run in headless mode
    user_data_dir="./user_data",      # Directory for persistent data
    user_agent=None,                  # Custom user agent string
    viewport={"width": 1920, "height": 1080},
    locale="en-US",                   # Browser locale
    timezone="America/Chicago",       # Browser timezone
    extensions=[],                    # Extension paths to load
    disable_animations=True,          # Disable CSS animations
    stealth_level="standard"          # "basic", "standard", or "maximum"
)
```

### Stealth Levels

- **basic**: Minimal anti-detection patches
- **standard**: Balanced protection (default)
- **maximum**: All available stealth patches

## Testing

The project uses pytest with coverage reporting:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_browser.py

# Run with coverage
pytest --cov=stealthkit --cov-report=html
```

**Coverage requirement**: Minimum 50% (configured in pyproject.toml)

## Code Quality

### Linting

The project uses ruff for fast Python linting:

```bash
# Run linter
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

### Type Checking

Pyright provides static type checking:

```bash
# Run type checker
pyright .
```

### Pre-commit Hook

A pre-commit hook is installed automatically that runs:
- Python compilation check
- Ruff linting
- Any type usage check (disallows `Any` type)
- Pyright type checking

The hook will block commits with issues. To test manually:

```bash
make githook
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `make lint`
6. Commit with conventional commits
7. Push and create a pull request

## License

MIT License - see LICENSE file for details

## Credits

Created by Josh Wren

## Related

- [Playwright Documentation](https://playwright.dev/python/)
- [playwright-stealth](https://github.com/AtuboDad/playwright_stealth)
- [structlog Documentation](https://www.structlog.org/)
