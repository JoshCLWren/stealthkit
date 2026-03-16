# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-03-14

### Added
- Initial release of stealthkit
- StealthBrowser async context manager for anti-detection browser automation
- PagePool for concurrent page management with semaphore-based concurrency control
- Anti-detection stealth patches via playwright-stealth integration
- Human behavior simulation (delays, mouse movements, scrolling)
- Cookie persistence (save/load to JSON)
- UserAgentGenerator for realistic user agent strings
- RateLimiter with exponential backoff for request throttling
- Comprehensive configuration via BrowserConfig dataclass
- Support for persistent browser context with user data
- Extension loading support (e.g., uBlock Origin)
- Structured logging with structlog
- Full async/await support throughout
- Type hints on all public APIs
- pytest test suite with 50%+ coverage
- Pre-commit hooks for code quality enforcement
