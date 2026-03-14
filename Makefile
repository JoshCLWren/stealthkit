.PHONY: help init lint pytest sync venv run githook install-githook

# Configuration
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
LIBDIR ?= $(PREFIX)/lib

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init:  ## Initialize project with new name (Usage: make init NAME=your-project)
	@if [ -z "$(NAME)" ]; then echo "Usage: make init NAME=your-project"; exit 1; fi
	$(eval PKG_DIR := $(subst -,_,$(NAME)))
	@echo "Initializing project as $(NAME) (package dir: $(PKG_DIR))..."
	@sed -i.bak 's/name = "python-starter-template"/name = "$(NAME)"/' pyproject.toml && rm pyproject.toml.bak
	@sed -i.bak 's/example_module/$(PKG_DIR)/g' pyproject.toml && rm pyproject.toml.bak
	@sed -i.bak 's/example_module/$(PKG_DIR)/g' .github/workflows/ci.yml && rm .github/workflows/ci.yml.bak
	@if [ -d "example_module" ]; then \
		echo "Renaming example_module to $(PKG_DIR)..."; \
		mv example_module $(PKG_DIR); \
		find . -type f -name "*.py" -not -path "./.venv/*" -exec sed -i.bak "s/from example_module/from $(PKG_DIR)/g" {} +; \
		find . -type f -name "*.py" -not -path "./.venv/*" -exec sed -i.bak "s/import example_module/import $(PKG_DIR)/g" {} +; \
		find . -type f -name "*.py.bak" -delete; \
	fi
	@if [ -f "main.py" ]; then \
		echo "Removing template main.py (library package)..."; \
		rm main.py; \
	fi
	@echo "Project initialized as $(NAME)"
	@echo "Run 'uv sync --group dev' to install dependencies"

lint:  ## Run code linting
	bash scripts/lint.sh

install-githook:  ## Install pre-commit hook for new developers
	@mkdir -p .git/hooks
	@cp .githooks/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hook installed to .git/hooks/pre-commit"

githook: install-githook  ## Run lint checks manually (installs pre-commit hook if missing)
	bash scripts/lint.sh

pytest:  ## Run tests
	pytest

sync:  ## Install dependencies
	uv sync --group dev

venv:  ## Create virtual environment
	uv venv

run:  ## Run the app
	python main.py
