# Architecture and engineering guide

## Project at a glance

`template-python` is a reusable baseline for Python 3.10+ projects. It provides
a small library and CLI example, environment-based settings, structured
logging, tests, documentation, container packaging, and pinned CI/CD
workflows.

The repository favors a small number of explicit rules enforced by the same
commands locally and in CI.

| Area | Source of truth |
| --- | --- |
| Package metadata and tool configuration | `pyproject.toml` |
| Resolved dependencies | `uv.lock` |
| Developer and CI commands | `Makefile` |
| Python compatibility and quality gates | `.github/workflows/test.yaml` |
| Documentation navigation and localization | `mkdocs.yml` |

## Repository map

| Path | Responsibility |
| --- | --- |
| `template_python/` | Reusable library code; must not depend on applications |
| `template_python/settings/` | Typed environment and `.env` configuration |
| `scripts/` | Application entry points that compose the library |
| `tests/` | Unit and behavior tests |
| `docs/` | English and Japanese MkDocs sources |
| `notebooks/` | Optional interactive examples |
| `.github/workflows/` | Test, documentation, container, and release automation |

Start with `pyproject.toml` and `Makefile`, then read
`scripts/template.py`, `template_python/core.py`,
`template_python/settings/project.py`, and the corresponding tests.

## Dependency rule

The intended dependency direction is:

```text
scripts (applications) -> template_python (library)
```

Applications may import and compose the library. Library modules must not
import `scripts`, directly or indirectly, including imports guarded by
`TYPE_CHECKING`. The import-linter contract in `pyproject.toml` enforces this
boundary for existing and newly added modules. Dependencies within the library
are intentionally unconstrained until a stable internal layering need appears.

## Runtime model

- `scripts/template.py` is the Typer CLI example and application composition
  root.
- `template_python/core.py` contains library behavior independent of the CLI.
- `ProjectSettings` reads `PROJECT_*` values from the environment and `.env`.
  Call `get_project_settings.cache_clear()` in tests or long-running processes
  that intentionally change settings after the first read.
- `get_logger()` owns one handler per named project logger, applies the current
  requested level on every call, and disables propagation to avoid duplicate
  output through the root logger.
- The Docker image runs `python -m template_python.core` by default. Compose
  overrides that command with a simple HTTP server for a container example.

## Design principles

1. **Keep dependency direction explicit.** Application code composes library
   code; reusable code never reaches back into an entry point.
2. **Use one command locally and in CI.** Add checks behind a Make target and
   invoke that target from CI instead of duplicating shell logic.
3. **Keep configuration at the boundary.** Read external configuration through
   typed settings and pass values into core behavior where practical.
4. **Make repeated calls safe.** Shared helpers such as logger and settings
   factories must not accumulate handlers or other process-global state.
5. **Prefer deterministic tooling.** Commit `uv.lock`, use `uv --locked`, and
   pin third-party GitHub Actions by commit SHA.
6. **Test observable contracts.** Verify behavior, dependency rules, and
   supported Python versions rather than implementation details alone.
7. **Keep the template replaceable.** Avoid project-specific infrastructure or
   domain abstractions until a generated project actually needs them.
8. **Surface failures.** Quality, type, architecture, documentation, and
   security checks must fail visibly instead of returning success-shaped
   fallbacks.

## Development workflow

```shell
make install-deps-dev
make fix
make ci-test
make ci-test-docs
```

`make ci-test` installs the CI dependency group and runs formatting checks,
mypy in strict mode, import-linter, Ruff, ty, Pyrefly, actionlint, zizmor, and
pytest. Python 3.13 runs the full quality gate in CI; Python 3.10 through 3.14
run compatibility tests. `make hooks-check` validates the configured prek
hooks.

Use `make docker-build`, `make docker-run`, and `make ci-test-docker` when a
Docker daemon is available. The Trivy target currently reports findings but
does not enforce a blocking severity threshold.

## Delivery model

- A push or pull request runs Python compatibility and quality workflows.
- A push to `main` publishes the MkDocs site.
- Version tags matching `v*` publish multi-platform images to Docker Hub and
  GitHub Container Registry.
- Azure Static Web Apps deployment is manual unless its push trigger is
  explicitly enabled.
- Dependabot checks uv, GitHub Actions, pre-commit, and Docker dependencies
  weekly.

Release workflows are delivery mechanisms, not substitutes for the test
workflow. Preserve least-privilege permissions and immutable action pins when
editing them.

## Change checklist

Before opening a pull request:

1. Put reusable behavior in `template_python/` and composition in `scripts/`.
2. Add or update focused tests for observable behavior.
3. Update `pyproject.toml` and regenerate `uv.lock` together for dependency
   changes.
4. Add reusable validation to `Makefile`, then wire CI to the Make target.
5. Update English and Japanese documentation when user-facing behavior or
   contributor rules change.
6. Run `make ci-test` and `make ci-test-docs`; run Docker checks for
   container-related changes.

## Known constraints

- The repository is a template, not a production service. Its CLI, notebook,
  HTTP server, and container command are examples to replace or extend.
- The library currently has no internal layer contract beyond the
  application/library boundary.
- Documentation depends on MkDocs plugins; any documentation engine migration
  must preserve multilingual output.
- Container vulnerability scanning is informative until an explicit blocking
  policy is adopted.
