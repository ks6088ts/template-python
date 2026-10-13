# Git
GIT_REVISION ?= $(shell git rev-parse --short HEAD)
GIT_TAG ?= $(shell git describe --tags --abbrev=0 --always | sed -e s/v//g)

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help

.PHONY: info
info: ## show information
	@echo "GIT_REVISION: $(GIT_REVISION)"
	@echo "GIT_TAG: $(GIT_TAG)"

.PHONY: install-deps-dev
install-deps-dev: ## install dependencies for development
	uv sync --locked --group dev
	@which actionlint || echo "install actionlint https://github.com/rhysd/actionlint"

.PHONY: install-hooks
install-hooks: ## install Git hooks
	uv run --locked prek install -f

.PHONY: install-deps-ci
install-deps-ci: ## install dependencies for CI checks
	uv sync --locked --group dev

.PHONY: install-deps
install-deps: ## install dependencies for production
	uv sync --locked --no-dev

.PHONY: format-check
format-check: ## format check
	uv run --locked ruff format --check .

.PHONY: format
format: ## format code
	uv run --locked ruff format .

.PHONY: fix
fix: ## apply auto-fixes
	uv run --locked ruff check --fix
	uv run --locked ruff format .

.PHONY: type-check
type-check: ## check types with mypy
	uv run --locked mypy --config-file pyproject.toml

.PHONY: lint
lint: type-check ## lint
	uv run --locked ruff check .
	actionlint
	uv run --locked zizmor --offline --strict-collection --min-severity high .

.PHONY: test
test: ## run tests
	uv run --locked pytest

.PHONY: build
build: ## build wheel and source distribution
	uv build --clear

.PHONY: package-check
package-check: build ## test the built wheel and installed CLI
	@wheel=$$(find dist -maxdepth 1 -name '*.whl' -type f -print -quit); \
		test -n "$$wheel"; \
		uv run --isolated --no-project --with "$$wheel" template-python hello --name Package | grep -Fx "Hello, Package!"; \
		uv run --isolated --no-project --with "$$wheel" python -m template_python hello --name Module | grep -Fx "Hello, Module!"

.PHONY: hooks-check
hooks-check: ## check all configured hooks
	uv run --locked prek run --all-files

.PHONY: ci-test
ci-test: install-deps-ci format-check lint test package-check ## run CI tests

.PHONY: update
update: ## update packages
	uv lock --upgrade

.PHONY: jupyterlab
jupyterlab: ## run Jupyter Lab
	uv run --locked --no-dev --group notebook jupyter lab

# ---
# Docker
# ---
DOCKER_REPO_NAME ?= ks6088ts
DOCKER_IMAGE_NAME ?= template-python
DOCKER_COMMAND ?= hello --name Container

# Tools
HADOLINT_VERSION ?= v2.15.1
TRIVY_VERSION ?= 0.74.0
TRIVY_CACHE_VOLUME ?= template-python-trivy-cache

.PHONY: docker-build
docker-build: ## build Docker image
	docker build \
		--pull \
		-t $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG) \
		--build-arg GIT_REVISION=$(GIT_REVISION) \
		--build-arg GIT_TAG=$(GIT_TAG) \
		.

.PHONY: docker-run
docker-run: ## run Docker container
	docker run --rm $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG) $(DOCKER_COMMAND)

.PHONY: docker-lint
docker-lint: ## lint Dockerfile
	docker run --rm -i hadolint/hadolint:$(HADOLINT_VERSION) < Dockerfile

.PHONY: docker-scan
docker-scan: ## scan Docker image
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(TRIVY_CACHE_VOLUME):/root/.cache/trivy \
		aquasec/trivy:$(TRIVY_VERSION) image \
		--exit-code 1 \
		--ignore-unfixed \
		--severity HIGH,CRITICAL \
		$(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG)

.PHONY: ci-test-docker
ci-test-docker: docker-lint docker-build docker-scan docker-run ## run CI test for Docker

# ---
# Docs
# ---

.PHONY: install-deps-docs
install-deps-docs: ## install dependencies for documentation
	uv sync --locked --no-dev --group docs

.PHONY: docs
docs: ## build documentation
	uv run --locked --no-dev --group docs mkdocs build

.PHONY: docs-serve
docs-serve: ## serve documentation
	uv run --locked --no-dev --group docs mkdocs serve

.PHONY: ci-test-docs
ci-test-docs: install-deps-docs docs ## run CI test for documentation
