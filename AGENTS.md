# Repository Guidelines

## Project Structure & Module Organization
The main application code lives in the `stealthkit` directory. The package provides Playwright stealth automation tools including browser context management, page pooling, anti-detection patches, human behavior simulation, cookie persistence, user agent generation, and rate limiting. Tooling metadata (`pyproject.toml`, `uv.lock`) defines project dependencies.

## Build, Test, and Development Commands
- `source .venv/bin/activate`: activate the virtual environment (do this once per session)
- `uv sync --all-extras`: install dependencies via uv
- `playwright install chromium`: install Playwright browser binaries
- `pytest`: run tests
- `make pytest`: run the test suite
- `make lint`: run ruff + pyright

## Getting Started
When setting up stealthkit:
1. Run `uv sync --all-extras` to install all dependencies
2. Run `playwright install chromium` to install Playwright browser binaries
3. Run `source .venv/bin/activate` to activate the virtual environment
4. Import and use stealthkit components in your project

## Git Worktrees (Parallel Work)
Use git worktrees to work on multiple cards in parallel without branch conflicts:
- Create a branch per card: `git switch -c card/short-slug`
- Add a worktree: `git worktree add ../stealthkit-<slug> card/short-slug`
- Work only in that worktree for the card; run tests there
- Keep the branch updated: `git fetch` then `git rebase origin/main` (or merge)
- When merged, remove it: `git worktree remove ../stealthkit-<slug>`
- Clean stale refs: `git worktree prune`
- WIP limit: 3 cards total in progress across all worktrees

## Test Coverage Requirements
- Current target: 50% coverage threshold (configured in `pyproject.toml`)
- Always run `pytest --cov=stealthkit --cov-report=term-missing` to check missing coverage
- When touching logic or input handling, ensure tests are added to maintain coverage
- Strategies for increasing coverage:
  - Add tests for remaining uncovered edge cases
  - Add tests for complex async code paths
  - Add tests for stealth patch application
  - Add tests for human behavior simulation
  - Add tests for rate limiting logic

## Coding Style & Naming Conventions
Follow standard PEP 8 spacing (4 spaces, 100-character soft wrap) and favor descriptive snake_case for functions and variables. Retain the current pattern of dataclasses for typed data containers and keep public functions annotated with precise types. Use async/await for all I/O operations. Prefer explicit helper names and guard callbacks with early returns rather than nesting.

Ruff configuration (from `pyproject.toml`):
- Line length: 100 characters
- Python version: 3.13
- Enabled rules: E, F, I, N, UP, B, C4, D
- Ignored: D203, D213, E501
- Code comments are discouraged - prefer clear code and commit messages

## Architecture Patterns

**Async-First Design**: All I/O operations (browser, file, network) use async/await. This enables high-concurrency browser automation and efficient resource management.

**Context Managers**: Use async context managers for resource management (e.g., `StealthBrowser`, `PagePool.acquire()`, `browser.page()`). This ensures proper cleanup of browser resources.

**Configuration via Dataclasses**: Use `BrowserConfig` dataclass for browser configuration. Provides type safety and validation.

**Semaphore-Based Concurrency**: `PagePool` uses `asyncio.Semaphore` to control concurrent page access, preventing resource exhaustion.

**Stealth Patches**: JavaScript code is injected via `apply_stealth()` to override browser properties that reveal automation.

**Human Behavior Simulation**: Functions like `human_like_delay()` and `random_mouse_movements()` add realistic delays and interactions to evade detection.

## Pre-commit Hook
A pre-commit hook is installed in `.git/hooks/pre-commit` that automatically runs:
- Check for type/linter ignores in staged files
- Run the shared lint script (`scripts/lint.sh`)

The lint script runs:
- Python compilation check
- Ruff linting
- Any type usage check (ruff ANN401 rule)
- Pyright type checking

The hook will block commits containing `# type: ignore`, `# noqa`, `# ruff: ignore`, or `# pylint: ignore`.

To test the hook manually: `make githook` or `bash scripts/lint.sh`

## Code Quality Standards
- Run linting after each change:
  - `make lint` or `bash scripts/lint.sh`
- Use specific types instead of `Any` in type annotations (ruff ANN401 rule)
- Run tests when you touch logic or input handling:
  - `pytest`
- Always write a regression test when fixing a bug
- If you break something while fixing it, fix both in the same PR
- Do not use in-line comments to disable linting or type checks
- Do not narrate your code with comments; prefer clear code and commit messages

## Style Guidelines
- Keep helpers explicit and descriptive (snake_case), and annotate public functions with precise types
- Use async context managers for resource cleanup
- Prefer `pathlib.Path` for file operations
- Use structlog for structured logging with context

## Branch Workflow
- Always create a feature branch from `main` before making changes:
  - `git checkout -b feature-name`
  - Use descriptive names like `fix-bug` or `add-feature`
- Push the feature branch to create a pull request
- After your PR is merged, update your local `main`:
  - `git checkout main`
  - `git pull`
  - Delete the merged branch: `git branch -d feature-name`

## Testing Guidelines
- Automated tests live in `tests/` and run with `python -m pytest` (or `make pytest`)
- When adding tests, keep `pytest` naming like `test_stealth_browser` or `test_page_pool`
- Always use appropriate fixtures from `conftest.py` for testing dependencies
- Test async functions with `pytest-asyncio`
- Mock Playwright objects in unit tests to avoid browser launches
- Test edge cases: browser failures, page crashes, network timeouts

## Commit & Pull Request Guidelines
- Use imperative, component-scoped commit messages (e.g., "Add feature X")
- Bundle related changes per commit
- PR summary should describe user impact and testing performed
- Attach screenshots when UI is affected

## stealthkit-Specific Guidelines

**Browser Lifecycle**: Always use `async with StealthBrowser() as browser:` to ensure proper cleanup. Never launch browsers without context management.

**Stealth Levels**: Use appropriate stealth levels:
- `basic`: Minimal overhead, suitable for low-security sites
- `standard`: Balanced protection (default)
- `maximum`: All patches applied, may impact performance

**Page Pool Management**: Always `await pool.initialize()` after creating a PagePool. Use `async with pool.acquire() as page:` for automatic page cleanup.

**Human Behavior**: Use `navigate_with_human_behavior()` instead of `page.goto()` to add realistic delays and interactions.

**Rate Limiting**: Always use `RateLimiter` when making multiple requests to avoid IP bans. Configure based on target site's rate limits.

**Cookie Persistence**: Save cookies after login and load them in subsequent sessions to avoid repeated authentication.

**User Agents**: Use `UserAgentGenerator` to generate realistic user agent strings that match your browser configuration.
