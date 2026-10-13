[![test](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml?query=branch%3Amain)
[![container-release](https://github.com/ks6088ts/template-python/actions/workflows/container-release.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/container-release.yaml)
[![docs](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml)

# template-python

A small, typed Python 3.12+ package and CLI template. It keeps the runtime
surface focused on [Typer](https://typer.tiangolo.com/) and
[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/),
uses [uv](https://docs.astral.sh/uv/) for reproducible environments and builds,
and provides optional container, documentation, notebook, and release assets.

## Quick start

Prerequisites:

- Python 3.12+
- uv 0.12.19
- GNU Make
- actionlint for the complete local quality gate
- Docker for container targets

```shell
make install-deps-dev
make ci-test
make ci-test-docs

uv run template-python hello --name Ada
uv run python -m template_python hello --name Ada
```

Configuration is loaded from `PROJECT_*` environment variables and an optional
`.env` file:

```shell
cp .env.template .env
PROJECT_LOG_LEVEL=DEBUG uv run template-python --verbose hello
```

## Project layout

| Path | Purpose |
| --- | --- |
| `src/template_python/` | Installable package, CLI, settings, and core behavior |
| `tests/` | Unit and CLI contract tests |
| `docs/` | English and Japanese documentation |
| `notebooks/` | Optional interactive example |
| `.github/workflows/` | Validation, docs, container, and release automation |

The core module is side-effect free. Configuration and logging are applied at
the CLI boundary, so package consumers can reuse core behavior without Typer,
environment, or process-global logging side effects.

## Development

```shell
make fix             # Ruff fixes and formatting
make lint            # Ruff, mypy, actionlint, and zizmor
make test            # pytest with branch coverage
make package-check   # build and run the wheel in isolation
make hooks-check     # run configured prek hooks
make ci-test         # complete Python quality gate
make ci-test-docs    # bilingual documentation build
make jupyterlab      # optional notebook environment
```

`uv.lock` is authoritative. Development, CI, documentation, and container
commands use locked dependency resolution.

## Containers

```shell
make docker-build
make docker-run
docker compose up --build
make ci-test-docker
```

The image installs the built wheel, runs as an unprivileged user, and starts the
same installed CLI used by package consumers. The Docker CI target runs
Hadolint, builds the image, blocks unfixed high/critical Trivy findings, and
executes the container.

## Optional assets

This template includes several independent assets. Remove any that a generated
project does not need:

- `notebooks/` and the `notebook` dependency group
- `docs/`, `mkdocs.yml`, and documentation workflows
- Dockerfile, Compose, and container workflows
- Docker Hub, GHCR, or Azure deployment workflows
- `.devcontainer/`

Removing an optional asset should also remove its dependency group, Make target,
workflow, badge, and documentation references.

## Releases

Tags matching `v*` publish the same multi-platform image to Docker Hub and GHCR.
Image tags are derived by `docker/metadata-action`; GHCR images also receive
GitHub artifact provenance. Keep the package version in `pyproject.toml`
aligned with a release tag before publishing.

See the [architecture and engineering guide](docs/architecture/README.md) for
design rules and the contributor checklist.
