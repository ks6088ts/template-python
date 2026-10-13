# template-python

`template-python` is a minimal Python 3.12+ package and CLI template.

```shell
make install-deps-dev
make ci-test
uv run template-python hello --name Ada
```

The package uses a `src/` layout, Typer for its installed CLI, Pydantic Settings
for validated `PROJECT_*` configuration, Ruff for formatting and linting, mypy
for strict type checking, and pytest for contract tests.

Optional assets include Docker/Compose, bilingual MkDocs documentation, a
Jupyter notebook, a Dev Container, Docker Hub and GHCR publishing, and Azure
Static Web Apps deployment. They consume the same package and commands but can
be removed independently.

Read the [architecture and engineering guide](architecture/README.md) before
changing package boundaries, dependencies, or delivery workflows.
