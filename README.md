[![test](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml?query=branch%3Amain)
[![docker-release](https://github.com/ks6088ts/template-python/actions/workflows/docker-release.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/docker-release.yaml)
[![ghcr-release](https://github.com/ks6088ts/template-python/actions/workflows/ghcr-release.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/ghcr-release.yaml)
[![docs](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# template-python

Opinionated GitHub template for modern Python projects with batteries
included: [`uv`](https://docs.astral.sh/uv/) for environment management,
[`ruff`](https://docs.astral.sh/ruff/) for formatting and linting,
[`mypy`](https://mypy.readthedocs.io/) for type-checking,
[`pytest`](https://docs.pytest.org/) for tests, a hardened multi-stage
Dockerfile, and a CI/CD pipeline that ships SARIF reports, signed images
(Sigstore cosign), build provenance attestations and SBOMs.

## Features

- 📦 **Reproducible environments** with `uv` and a committed `uv.lock`.
- 🧹 **Strict linting** via Ruff with `B`/`S`/`SIM`/`RUF`/`PTH` rule sets.
- 🔍 **Type checking** with `mypy` (strict) plus the experimental
    [`ty`](https://github.com/astral-sh/ty) and
    [`pyrefly`](https://github.com/facebook/pyrefly) for early signal.
- 🧪 **Multi-version testing** matrix (Python 3.10–3.13 on Ubuntu, plus a
    macOS and Windows smoke run) and coverage reporting.
- 🛡️ **Security tooling baked in**: GitHub Code Scanning (CodeQL Default
    Setup) at the repository level, plus local helpers — `make security`
    runs `pip-audit` against the production lockfile and the `gitleaks`
    pre-commit hook blocks accidental secret commits. Container images
    are scanned with hadolint and Trivy in the `docker` workflow.
- 🚢 **Supply-chain ready releases**: multi-arch images with SBOM,
    provenance, and Sigstore-signed digests.
- 🧰 **Vanilla Typer skeleton** under [`scripts/template.py`](scripts/template.py)
    that you can copy and adapt to expose your own command-line interface.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [GNU Make](https://www.gnu.org/software/make/)
- (Optional) [Docker](https://docs.docker.com/get-docker/) and
    [`actionlint`](https://github.com/rhysd/actionlint) for the local CI.

## Quick start

```shell
# Install all dev/test/docs tooling and pre-commit hooks
make install-deps-dev

# Format, lint, type-check, and test
make ci-test

# Run the bundled Typer skeleton
uv run python scripts/template.py hello --name "World" --verbose
```

## Development

```shell
make help              # list all available targets
make format            # ruff format
make fix               # ruff format + ruff check --fix
make lint              # ruff + mypy + (ty|pyrefly|actionlint best-effort)
make type-check        # mypy only
make test              # pytest with coverage
make security          # pip-audit against the production lockfile
make docs-serve        # live docs preview at http://127.0.0.1:8000
```

The default branch enforces the same checks via the
[`test`](.github/workflows/test.yaml) workflow on every push and pull
request.

## Docker

The image is built with a multi-stage `uv` workflow and runs as a
non-privileged user (`UID 10001`). The default command runs
`python -m template_python.core` — override it with your own entry point
when you build a real application on top of this template.

```shell
make docker-build
make docker-run

# Run a different command in the same image
docker run --rm ks6088ts/template-python:$(git describe --tags --abbrev=0 --always | sed 's/^v//') \
    python -c "import template_python; print(template_python.__version__)"

# Lint and scan the image
make docker-lint
make docker-scan
```

A minimal Compose file is provided as a smoke-test of the runtime image:

```shell
docker compose up --build
```

## Releases & supply chain

- Tag a commit with `vX.Y.Z` to trigger:
    - `ghcr-release.yaml` — push a multi-arch image to GHCR with SBOM,
        provenance and a `cosign sign` keyless signature.
    - `docker-release.yaml` — push the same image to Docker Hub with the
        same supply-chain artefacts (requires `DOCKERHUB_USERNAME` /
        `DOCKERHUB_TOKEN` secrets).
- `dependabot.yaml` keeps GitHub Actions, Python, Docker base image, and
    devcontainer features up to date weekly.

### Verifying a published image

```shell
cosign verify \
    --certificate-identity-regexp 'https://github.com/ks6088ts/template-python/.+' \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com \
    ghcr.io/ks6088ts/template-python:<tag>
```

## Deployment

### Docker Hub

To publish the docker image to Docker Hub, [create an access
token](https://app.docker.com/settings/personal-access-tokens/create) and
configure repository secrets:

```shell
gh secret set DOCKERHUB_USERNAME --body "$DOCKERHUB_USERNAME"
gh secret set DOCKERHUB_TOKEN --body "$DOCKERHUB_TOKEN"
```

### Azure Static Web Apps

```shell
RESOURCE_GROUP_NAME=your-resource-group-name
SWA_NAME=your-static-web-app-name

# Create a static app
az staticwebapp create --name $SWA_NAME --resource-group $RESOURCE_GROUP_NAME

# Retrieve the API key
AZURE_STATIC_WEB_APPS_API_TOKEN=$(az staticwebapp secrets list \
    --name $SWA_NAME --query "properties.apiKey" -o tsv)

# Set the API key as a GitHub secret
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "$AZURE_STATIC_WEB_APPS_API_TOKEN"
```

References:

- [Deploying to Azure Static Web App](https://docs.github.com/en/actions/use-cases-and-examples/deploying/deploying-to-azure-static-web-app)
- [`az staticwebapp create`](https://learn.microsoft.com/en-us/cli/azure/staticwebapp?view=azure-cli-latest#az-staticwebapp-create)

## License

Distributed under the [MIT License](LICENSE).
