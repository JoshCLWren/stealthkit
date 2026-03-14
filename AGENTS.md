# Repository Guidelines

## Project Structure & Module Organization
The main application code lives in the `example_module` directory (which can be renamed via `make init`). The entrypoint is `main.py`. Tooling metadata (`pyproject.toml`, `uv.lock`) defines project dependencies. Expect any future modules (tests, components, helpers) to sit alongside these files unless a new package directory is created.

## Build, Test, and Development Commands
- `make init NAME=your-project`: initialize the template with your project name (renames module and updates config).
- `source .venv/bin/activate`: activate the virtual environment (do this once per session).
- `uv sync --all-extras`: install dependencies via uv.
- `python main.py`: run the main entrypoint.
- `pytest`: run tests.
- `make pytest`: run the test suite.
- `make lint`: run ruff.

## Getting Started
When cloning this template for a new project:
1. Run `make init NAME=your-project` to rename the module and update config
2. Run `uv sync --all-extras` to install all dependencies
3. Run `source .venv/bin/activate` to activate the virtual environment
4. Start building your project!

## Git Worktrees (Parallel Work)
Use git worktrees to work on multiple cards in parallel without branch conflicts:
- Create a branch per card: `git switch -c card/short-slug`
- Add a worktree: `git worktree add ../project-<slug> card/short-slug`
- Work only in that worktree for the card; run tests there.
- Keep the branch updated: `git fetch` then `git rebase origin/main` (or merge).
- When merged, remove it: `git worktree remove ../project-<slug>`
- Clean stale refs: `git worktree prune`
- WIP limit: 3 cards total in progress across all worktrees.

## Test Coverage Requirements
- Current target: 96% coverage threshold (configured in `pyproject.toml`)
- Always run `pytest --cov=example_module --cov-report=term-missing` to check missing coverage
- When touching logic or input handling, ensure tests are added to maintain coverage
- Strategies for increasing coverage:
  - Add tests for remaining uncovered edge cases
  - Add tests for complex error handling paths
  - Add tests for platform-specific code paths

## Coding Style & Naming Conventions
Follow standard PEP 8 spacing (4 spaces, 100-character soft wrap) and favor descriptive snake_case for functions and variables. Retain the current pattern of dataclasses for typed data containers and keep public functions annotated with precise types. Prefer explicit helper names and guard callbacks with early returns rather than nesting.

Ruff configuration (from `pyproject.toml`):
- Line length: 100 characters
- Python version: 3.13
- Enabled rules: E, F, I, N, UP, B, C4, D, ANN401
- Ignored: D203, D213, E501
- Code comments are discouraged - prefer clear code and commit messages

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
- Always write a regression test when fixing a bug.
- If you break something while fixing it, fix both in the same PR.
- Do not use in-line comments to disable linting or type checks.
- Do not narrate your code with comments; prefer clear code and commit messages.

## Style Guidelines
- Keep helpers explicit and descriptive (snake_case), and annotate public
  functions with precise types.
- Avoid shell-specific shortcuts; prefer Python APIs and `pathlib.Path` helpers.

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
- Automated tests live in `tests/` and run with `python -m pytest` (or `make pytest`).
- When adding tests, keep `pytest` naming like `test_example_function`.
- Always use appropriate fixtures from `conftest.py` for testing dependencies.

## Commit & Pull Request Guidelines
- Use imperative, component-scoped commit messages (e.g., "Add feature X")
- Bundle related changes per commit
- PR summary should describe user impact and testing performed
- Attach screenshots when UI is affected
