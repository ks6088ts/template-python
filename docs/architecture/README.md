# Architecture and engineering guide

Use this guide when deciding where code belongs, adding a dependency, or changing
delivery assets. For executable procedures and troubleshooting, use the
[development guide](../development.md).

## Default design

The repository has one installable package and one thin application boundary:

```text
CLI (Typer, settings, logging) -> core behavior (values and specific exceptions)
```

`src/template_python/core.py` contains deterministic behavior with no
environment, logging, or CLI side effects. `cli.py` loads settings, configures
logging, and calls the core. `__init__.py` exports reusable behavior without
importing the CLI; `__main__.py` is only an entry point.

This keeps library consumers from needing to understand Typer, environment
loading, or process-global logging just to call a function.

## Where to change code

| Change | Primary location | Contract to test |
| --- | --- | --- |
| Reusable behavior | `src/template_python/core.py` or a focused new module | Values, normalization, and specific exceptions in `tests/test_core.py` or a matching new test module |
| Command, option, or user-facing error | `src/template_python/cli.py` | stdout, stderr, and exit codes in `tests/test_cli.py` |
| Environment configuration | `src/template_python/settings.py` and `.env.template` | Defaults, valid values, and rejection in `tests/test_settings.py` |
| Logging setup | `src/template_python/logging.py` | Level validation and emitted messages in `tests/test_logging.py` |
| Public library API | `src/template_python/__init__.py` | Import and call the public API without initializing the CLI |
| Build or dependency change | `pyproject.toml` and `uv.lock` | Installed wheel behavior via `make package-check` |

## Keep the cognitive cost small

Defaults are deliberate. Change them for a concrete requirement, not a possible
future one.

| Decision | Default | Reconsider when... |
| --- | --- | --- |
| Where to put new behavior | A named function in a focused package module | A concrete external I/O requirement needs an application adapter |
| Whether to share code | Keep it local and name it for its responsibility | Multiple real call sites have the same stable behavior |
| Whether to add a class or framework | Prefer functions and explicit arguments | State or lifecycle ownership is necessary and simpler composition is insufficient |
| Whether to add a dependency or tool | Use the standard library and existing toolchain | A distinct, measurable gap justifies its runtime and maintenance cost |
| Whether to add an optional asset | Leave it unused or remove it | The project's actual delivery or development needs require it |

- Avoid generic `utils` / `common` buckets, base-class hierarchies, service
  locators, and speculative dependency-injection frameworks.
- Use names that reveal inputs, outputs, and responsibility. A reader should not
  need to follow several layers to understand a small operation.
- Return values or raise specific exceptions. Do not turn failures into
  success-shaped defaults, suppress errors broadly, or log secrets.
- Keep one authoritative procedure for each task. Link to it rather than
  copying commands into several documents or workflows.

For a non-obvious decision, include the problem, simplest alternative, chosen
trade-off, and verification in the PR description. A separate design document
is only useful when the rationale needs to outlive the change.

## Sources of truth

| Concern | Source |
| --- | --- |
| Metadata, dependencies, tool configuration | `pyproject.toml` |
| Resolved dependency versions | `uv.lock` |
| Local and CI commands | `Makefile` |
| Minimum Python / tested versions | `pyproject.toml` / `.github/workflows/test.yaml` |
| Configuration schema / example overrides | `src/template_python/settings.py` / `.env.template` |
| Container behavior | `Dockerfile` and `compose.yml` |
| Documentation navigation | `mkdocs.yml` |

Update declarations and derived assets together. Dependency declarations change
in `pyproject.toml`; regenerate `uv.lock` with `uv lock`. CI should call Make
targets instead of maintaining another implementation of the same checks.

## Runtime rules

- The public package must remain importable without configuring logging or
  reading environment variables.
- Core modules do not depend on Typer or settings. The CLI translates their
  values and exceptions into user-facing output and exit codes.
- `ProjectSettings` owns `PROJECT_*` environment and optional `.env` loading.
  Do not add a second dotenv loader.
- Configure root logging once in the CLI callback. Library modules only obtain
  named loggers.
- Expose commands through `[project.scripts]`; keep `python -m template_python`
  as a convenience path.

## Quality gate

Use the [checks by change type](../development.md#checks-by-change-type).
The Python gate checks formatting, types, lint, workflow rules, and all tests
with branch coverage of at least 95%. It builds wheel and sdist, then runs the
installed wheel's CLI and module entry point in isolation. It does not smoke-test
the sdist installation.

Test observable contracts, including failure paths, instead of coupling tests
to internal structure. Keep stdout, stderr, exit codes, and import-time behavior
stable unless the change explicitly requires a compatibility break.

## Delivery

- Pull requests and supported branches run Python and container validation.
- `main` publishes the bilingual documentation with GitHub Pages artifacts.
- `v*` tags publish multi-platform images to Docker Hub and GHCR.
- GHCR releases include build provenance tied to the pushed digest.
- Azure Static Web Apps deployment remains manual.

The release workflow verifies that the tag is exactly `v` followed by the
`pyproject.toml` version before publishing. It requires `DOCKERHUB_USERNAME` and
`DOCKERHUB_TOKEN` secrets for Docker Hub; GHCR uses the workflow's GitHub token.
The manual site workflow requires `AZURE_STATIC_WEB_APPS_API_TOKEN`. These
credentials are not required for local development. PyPI publishing is not
configured.

Third-party actions are pinned by commit SHA. Workflows use explicit minimum
permissions, disabled checkout credentials, bounded timeouts, and cancellation
only for superseded non-release runs.

## Adopting the template

Do this once when creating a project, before enabling publishing.

1. Set the project identity: distribution name, description, version, URLs, and
   console script in `pyproject.toml`. Confirm the license is appropriate.
2. If renaming the import package, rename `src/template_python/` and update
   imports, test references, the script target, module-entry commands, and tool
   paths such as coverage. Preserve `py.typed` for the typed package.
3. Update settings defaults, `.env.template`, notebook examples, Makefile smoke
   commands and image defaults, Dockerfile entry point and labels, Compose,
   Dev Container name, documentation URLs, workflow image names, and README
   badges. Distribution names use hyphens; Python import names use underscores.
4. Remove unneeded assets using the table below; do not leave dead CI references.
5. Run `uv lock` and checks for the retained assets. Verify the renamed installed
   CLI, not just a direct source import.
6. Configure repository publishing settings and secrets only for retained
   delivery workflows. Match the package version to the release tag.

### Optional assets

Notebook, docs, containers, registries, Azure, and the Dev Container are
independent examples. They must consume the installed package rather than
creating alternative application behavior.

| Remove this asset | Also remove or update |
| --- | --- |
| Notebook | `notebooks/`, the `notebook` dependency group, and `jupyterlab` Make target |
| Documentation site | `docs/`, `mkdocs.yml`, the `docs` group and Make targets, both site deployment workflows, and the docs command in `test.yaml` |
| Containers | Dockerfile, Compose, `.dockerignore`, Docker Make targets/variables, and container validation/release workflows |
| Registry publishing only | Unneeded jobs or the container-release workflow; keep local container checks if still useful |
| Manual site deployment only | `azure-static-web-app.yaml` and deployment references |
| Dev Container | `.devcontainer/` and setup references |

In the same change, regenerate the lock file if groups changed and clean up
badges, links, and guide entries. Avoid keeping an unused workflow that requires
credentials.

MkDocs is intentionally constrained below version 2 while multilingual output
depends on the MkDocs 1 plugin ecosystem.

## Change checklist

- [ ] The change has one clear purpose and uses the module boundaries above.
- [ ] Tests cover the expected values and failures; compatibility changes are explicit.
- [ ] Dependency declarations, lock file, and affected delivery assets agree.
- [ ] Commands reuse existing Make targets; any new tool fills a demonstrated gap.
- [ ] Affected English and Japanese documentation is updated without duplicating procedures.
- [ ] Checks for each changed area pass, including installed-package checks where relevant.
