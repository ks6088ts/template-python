[![test](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml?query=branch%3Amain)
[![container-release](https://github.com/ks6088ts/template-python/actions/workflows/container-release.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/container-release.yaml)
[![docs](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml)

# template-python

[日本語ガイド](docs/index.ja.md) | [Documentation](https://ks6088ts-labs.github.io/template-python)

A small, typed Python package and CLI template for starting a library or
command-line application without assembling a toolchain from scratch.
[Typer](https://typer.tiangolo.com/) handles the CLI,
[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
validates configuration, and [uv](https://docs.astral.sh/uv/) manages the locked
environment. Containers, notebooks, and deployment are optional.

## Quick start

Start with **Python 3.12+**, **uv 0.12.19**, and **GNU Make**. Python 3.13 is the
full CI baseline; compatibility tests also cover 3.12 and 3.14.
See the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
if uv is not installed. Docker, actionlint, and deployment credentials are not
needed to run the example or unit tests.

From a terminal:

```shell
git clone https://github.com/ks6088ts/template-python.git
cd template-python
make install-deps-dev
uv run --locked template-python hello --name Ada
```

Expected output:

```text
Hello, Ada!
```

Then run `make test`. No virtual environment activation or `.env` file is
required. The equivalent module entry point is
`uv run --locked python -m template_python hello --name Ada`.

## Choose your next task

Read only the guide needed for the change:

| I want to... | Start here |
| --- | --- |
| Change behavior, run checks, or resolve a setup failure | [Development guide](docs/development.md) |
| Decide where code belongs or whether to add an abstraction | [Architecture and engineering guide](docs/architecture/README.md) |
| Configure the CLI | [Configuration reference](docs/development.md#configuration) |
| Turn this template into a new project | [Template adoption checklist](docs/architecture/README.md#adopting-the-template) |
| Preview or edit documentation | [Documentation workflow](docs/development.md#documentation) |

## Project map

```text
CLI (settings + logging) -> reusable core behavior
```

| Location | Responsibility |
| --- | --- |
| [core.py](src/template_python/core.py) | Deterministic behavior, independent of CLI and environment |
| [cli.py](src/template_python/cli.py) | Commands, user-facing errors, and application setup |
| [settings.py](src/template_python/settings.py), [logging.py](src/template_python/logging.py) | Configuration validation and logging setup |
| [tests/](tests/) | Behavior and CLI contract tests |
| [Makefile](Makefile) | Supported local and CI commands; run `make help` to list them |
| [pyproject.toml](pyproject.toml), [uv.lock](uv.lock) | Dependencies, tool configuration, and resolved versions |
| [docs/](docs/) | Task-oriented guides in English and Japanese |

## Before submitting a change

| Changed area | Check |
| --- | --- |
| Python, dependencies, or workflows | `make ci-test` |
| Documentation | `make ci-test-docs` |
| Container assets | `make ci-test-docker` |

The Python gate requires [actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md)
on `PATH`. The container gate requires a running Docker daemon. If a change spans
areas, run each corresponding check. See the
[development guide](docs/development.md#checks-by-change-type) for focused checks
and Git hooks.

## Optional assets and releases

Use these only when your project needs them:

| Asset | Entry point |
| --- | --- |
| Container example | `make docker-build docker-run` or `docker compose up --build` |
| Documentation site | `make docs-serve` |
| Notebook example | `make jupyterlab` |
| VS Code Dev Container | [.devcontainer/](.devcontainer/) |
| Image publishing and site deployment | [.github/workflows/](.github/workflows/) |

No registry or cloud account is needed for local development. Remove unused
assets and their related dependencies, Make targets, workflows, and links
together; follow the [adoption checklist](docs/architecture/README.md#adopting-the-template).

Tags matching `v*` publish images to Docker Hub and GHCR only after checking that
the tag matches the package version. This template does not publish to PyPI.
See [delivery rules](docs/architecture/README.md#delivery) before enabling releases.

## License

[MIT](LICENSE).
