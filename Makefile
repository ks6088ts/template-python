SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

# Git
GIT_REVISION ?= $(shell git rev-parse --short HEAD)
GIT_TAG ?= $(shell git describe --tags --abbrev=0 --always | sed -e 's/^v//')

# Container images used as tools. Pin by digest; refresh with
# `docker buildx imagetools inspect <image>:<tag>`.
HADOLINT_IMAGE ?= hadolint/hadolint:v2.15.1@sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d
TRIVY_IMAGE ?= aquasec/trivy:0.76.1@sha256:790fd66d1697395d8693d1acaa1ea702406a20f109b6fc7bac8db623eca6c06c
GITLEAKS_IMAGE ?= zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f
TRIVY_CACHE_VOLUME ?= template-python-trivy-cache

# Lowest supported Python, used with the lowest declared direct dependencies.
LOWEST_PYTHON ?= 3.12
LOWEST_VENV ?= build/venv-lowest

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help

.PHONY: info
info: ## show information
	@echo "GIT_REVISION: $(GIT_REVISION)"
	@echo "GIT_TAG: $(GIT_TAG)"
	@echo "PACKAGE_VERSION: $$(uv version --short)"

# ---
# Python
# ---

.PHONY: install-deps-dev
install-deps-dev: ## install dependencies for development
	uv sync --locked --group dev

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
	uv run --locked ruff check --fix .
	uv run --locked ruff format .

.PHONY: type-check
type-check: ## check types with mypy
	uv run --locked mypy

.PHONY: lint
lint: type-check ## lint Python code and GitHub workflows
	uv run --locked ruff check .
	uv run --locked actionlint
	uv run --locked zizmor --offline --min-severity low .

.PHONY: test
test: ## run tests with coverage
	uv run --locked pytest

.PHONY: test-lowest
test-lowest: ## run tests with the lowest supported Python and direct dependency versions
	uv venv --quiet --clear --python $(LOWEST_PYTHON) $(LOWEST_VENV)
	uv pip install --quiet --python $(LOWEST_VENV) --resolution lowest-direct --group test .
	$(LOWEST_VENV)/bin/python -m pytest -p no:cacheprovider

.PHONY: build
build: ## build wheel and source distribution
	uv build --clear

.PHONY: package-check
package-check: build ## test the built wheel and installed CLI
	@wheel=$$(find dist -maxdepth 1 -name '*.whl' -type f -print -quit); \
		test -n "$$wheel"; \
		uv run --isolated --no-project --with "$$wheel" template-python hello --name Package | grep -Fx "Hello, Package!"; \
		uv run --isolated --no-project --with "$$wheel" python -m template_python hello --name Module | grep -Fx "Hello, Module!"; \
		uv run --isolated --no-project --with "$$wheel" template-python --version | grep -Fx "template-python $$(uv version --short)"

.PHONY: hooks-check
hooks-check: ## run all configured Git hooks against all files
	uv run --locked prek run --all-files

.PHONY: ci-test
ci-test: install-deps-ci format-check lint test package-check ## run CI tests

.PHONY: update
update: ## upgrade all locked packages
	uv lock --upgrade

.PHONY: jupyterlab
jupyterlab: ## run Jupyter Lab
	uv run --locked --no-dev --group notebook jupyter lab

# ---
# Security
# ---

.PHONY: audit
audit: ## audit locked dependencies for known vulnerabilities
	@requirements=$$(mktemp); trap 'rm -f "$$requirements"' EXIT; \
		uv export --quiet --locked --all-groups --no-emit-project --format requirements-txt --output-file "$$requirements"; \
		uv run --locked pip-audit --requirement "$$requirements" --require-hashes --disable-pip --strict --progress-spinner off

.PHONY: secret-scan
secret-scan: ## scan the Git history for secrets (requires Docker)
	docker run --rm \
		-v "$(CURDIR):/repo:ro" \
		-e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
		$(GITLEAKS_IMAGE) git /repo --redact --no-banner --verbose

.PHONY: security-scan
security-scan: ## scan files for vulnerabilities, misconfigurations, and secrets (requires Docker)
	docker run --rm \
		-v "$(CURDIR):/src:ro" \
		-v $(TRIVY_CACHE_VOLUME):/root/.cache/trivy \
		$(TRIVY_IMAGE) fs \
		--skip-version-check \
		--scanners vuln,misconfig,secret \
		--skip-dirs /src/.venv,/src/build,/src/dist,/src/site \
		--exit-code 1 \
		--ignore-unfixed \
		--severity HIGH,CRITICAL \
		/src

.PHONY: ci-test-security
ci-test-security: install-deps-ci audit secret-scan security-scan ## run CI security scans

# ---
# Docker
# ---
DOCKER_REPO_NAME ?= ks6088ts
DOCKER_IMAGE_NAME ?= template-python
DOCKER_COMMAND ?= hello --name Container

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
	docker run --rm -i $(HADOLINT_IMAGE) < Dockerfile

.PHONY: docker-scan
docker-scan: ## scan Docker image
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(TRIVY_CACHE_VOLUME):/root/.cache/trivy \
		$(TRIVY_IMAGE) image \
		--skip-version-check \
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
	uv run --locked --no-dev --group docs mkdocs build --strict

.PHONY: docs-serve
docs-serve: ## serve documentation
	uv run --locked --no-dev --group docs mkdocs serve

.PHONY: ci-test-docs
ci-test-docs: install-deps-docs docs ## run CI test for documentation
