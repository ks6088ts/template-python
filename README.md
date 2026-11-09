[![test](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml?query=branch%3Amain)
[![security](https://github.com/ks6088ts/template-python/actions/workflows/security.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/security.yaml?query=branch%3Amain)
[![codeql](https://github.com/ks6088ts/template-python/actions/workflows/codeql.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/codeql.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml?query=branch%3Amain)
[![release](https://github.com/ks6088ts/template-python/actions/workflows/release.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/release.yaml)
[![docs](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/ks6088ts/template-python/badge)](https://scorecard.dev/viewer/?uri=github.com/ks6088ts/template-python)

# template-python

[日本語ガイド](docs/index.ja.md) | [Documentation](https://ks6088ts-labs.github.io/template-python)

A small, typed Python CLI template with a production-grade toolchain: static
analysis, tests with coverage, vulnerability and secret scanning, hardened
containers, and CI/CD with signed releases.
[Typer](https://typer.tiangolo.com/) handles the CLI,
[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
validates configuration, and [uv](https://docs.astral.sh/uv/) manages the locked
environment. Containers, notebooks, and deployment are optional.

## Quick start

You need **uv 0.13.x** (`>=0.13.1,<0.14`, declared in `pyproject.toml`) and
**GNU Make**. uv installs the default **Python 3.14** from `.python-version`;
Python **3.12–3.15** are supported and tested.
See the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
if uv is not installed. Docker and deployment credentials are not needed to run
the example or the Python quality gate.

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

Then run `make ci-test`. No virtual environment activation or `.env` file is
required. Other entry points:

```shell
uv run --locked template-python --version
uv run --locked template-python config
uv run --locked python -m template_python hello --name Ada
```

## Choose your next task

| I want to... | Start here |
| --- | --- |
| Change behavior, run checks, or resolve a setup failure | [Development guide](docs/development.md) |
| Decide where code belongs or whether to add an abstraction | [Architecture and engineering guide](docs/architecture/README.md) |
| Configure the CLI | [Configuration reference](docs/development.md#configuration) |
| Understand the security and release pipeline | [Security and supply chain](docs/architecture/README.md#security-and-supply-chain) |
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
| [settings.py](src/template_python/settings.py), [log.py](src/template_python/log.py) | Configuration validation and logging setup |
| [tests/](tests/) | Behavior and CLI contract tests |
| [Makefile](Makefile) | Supported local and CI commands; run `make help` to list them |
| [pyproject.toml](pyproject.toml), [uv.lock](uv.lock) | Dependencies, tool configuration, and resolved versions |
| [.github/](.github/) | CI/CD workflows, Dependabot, and contribution templates |
| [docs/](docs/) | Task-oriented guides in English and Japanese |

## Before submitting a change

| Changed area | Check |
| --- | --- |
| Python, dependencies, or workflows | `make ci-test` |
| Dependencies | `make audit` and `make test-lowest` |
| Documentation | `make ci-test-docs` |
| Container assets | `make ci-test-docker` |

Docker-based checks (`ci-test-docker`, `secret-scan`, `security-scan`) require a
running Docker daemon. See the
[development guide](docs/development.md#checks-by-change-type) for focused
checks and Git hooks, and [CONTRIBUTING.md](CONTRIBUTING.md) for the pull
request flow.

## Optional assets and releases

| Asset | Entry point |
| --- | --- |
| Container example | `make docker-build docker-run` or `docker compose up --build` |
| Documentation site | `make docs-serve` |
| Notebook example | `make jupyterlab` |
| VS Code Dev Container | [.devcontainer/](.devcontainer/) |
| Image publishing and site deployment | [.github/workflows/](.github/workflows/) |

No registry or cloud account is needed for local development. Tags matching
`v*` publish a multi-platform image with an SBOM and build provenance to GHCR
after verifying that the tag equals `v` + the package version. This template does
not publish to PyPI. See [delivery](docs/architecture/README.md#delivery) before
enabling releases, and remove unused assets with the
[adoption checklist](docs/architecture/README.md#adopting-the-template).

## Security

Report vulnerabilities privately; see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE).
