.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help

.PHONY: install-deps-dev
install-deps-dev: ## install dependencies for development
	poetry install
	poetry run pre-commit install

.PHONY: install-deps
install-deps: ## install dependencies for production
	poetry install --only-root

.PHONY: format-check
format-check: ## format check
	poetry run black . --check --verbose

.PHONY: format
format: ## format code
	poetry run black . --verbose

.PHONY: lint
lint: ## lint
	poetry run ruff check .

.PHONY: test
test: ## run tests
	poetry run pytest

.PHONY: ci-test
ci-test: install-deps-dev format-check lint test ## run CI tests
