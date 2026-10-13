# Architecture and engineering guide

## Design

The repository has one installable package and one thin application boundary:

```text
CLI (Typer, settings, logging) -> core behavior
```

`src/template_python/core.py` contains deterministic behavior with no
environment, logging, or CLI side effects. `cli.py` composes settings and
logging, then calls the core. New reusable behavior belongs in focused package
modules; infrastructure stays at an application boundary.

Avoid generic `utils`, `common`, base-class hierarchies, service locators, and
dependency-injection frameworks. Add a shared abstraction only after multiple
concrete call sites demonstrate the same stable need.

## Sources of truth

| Concern | Source |
| --- | --- |
| Metadata, dependencies, tool configuration | `pyproject.toml` |
| Resolved dependencies | `uv.lock` |
| Local and CI commands | `Makefile` |
| Supported Python versions | `pyproject.toml` and `test.yaml` |
| Container behavior | `Dockerfile` and `compose.yml` |
| Documentation navigation | `mkdocs.yml` |

The lock file is committed and commands use `--locked`. Update
`pyproject.toml` and `uv.lock` together.

## Runtime rules

- The public package must remain importable without configuring logging or
  reading environment variables.
- Core functions return values or raise specific exceptions; the CLI translates
  them into user-facing output and exit codes.
- `ProjectSettings` owns `PROJECT_*` environment and optional `.env` loading.
  Do not add a second dotenv loader.
- Configure root logging once in the CLI callback. Library modules only obtain
  named loggers.
- Expose commands through `[project.scripts]`; keep `python -m template_python`
  as a convenience path.

## Quality gate

```shell
make ci-test
make ci-test-docs
```

The Python gate runs Ruff formatting/linting, mypy strict, actionlint, zizmor,
pytest with branch coverage, and wheel/sdist smoke tests. Compatibility jobs run
tests on every supported Python version. Pre-commit-compatible hooks are
validated separately with `make hooks-check`.

Do not add a second tool for the same responsibility without removing the
existing one or documenting a distinct measurable gap.

## Delivery

- Pull requests and supported branches run Python and container validation.
- `main` publishes the bilingual documentation with GitHub Pages artifacts.
- `v*` tags publish multi-platform images to Docker Hub and GHCR.
- GHCR releases include build provenance tied to the pushed digest.
- Azure Static Web Apps deployment remains manual.

Third-party actions are pinned by commit SHA. Workflows use explicit minimum
permissions, disabled checkout credentials, bounded timeouts, and cancellation
only for superseded non-release runs.

## Optional assets

Notebook, docs, containers, registries, Azure, and the Dev Container are
independent examples. They must consume the installed package rather than
creating alternative application behavior. If an asset is removed, delete its
dependencies, commands, workflows, and documentation in the same change.

MkDocs is intentionally constrained below version 2 while multilingual output
depends on the MkDocs 1 plugin ecosystem.

## Change checklist

1. Keep core behavior deterministic and application concerns at the boundary.
2. Add focused tests for outputs, errors, CLI exits, and configuration.
3. Update `pyproject.toml` and `uv.lock` together.
4. Reuse Make targets from CI instead of duplicating shell logic.
5. Update English and Japanese documentation together.
6. Run `make ci-test` and `make ci-test-docs`.
7. Run Docker checks for container-related changes.
8. Inspect built distributions and dependency graphs before release.
