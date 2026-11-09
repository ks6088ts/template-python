# Architecture and engineering guide

Use this guide when deciding where code belongs, adding a dependency, or changing
delivery assets. For executable procedures and troubleshooting, use the
[development guide](../development.md).

## Default design { #default-design }

The repository has one installable package and one thin application boundary:

```text
CLI (Typer, settings, logging) -> core behavior (values and specific exceptions)
```

`src/template_python/core.py` contains deterministic behavior with no
environment, logging, or CLI side effects. `cli.py` loads settings once in the
Typer callback, configures logging, stores the settings on the Click context
(`ctx.obj`) for commands, and calls the core. `__init__.py` exports reusable
behavior and `__version__` without importing the CLI; `__main__.py` is only a
guarded entry point.

This keeps library consumers from needing to understand Typer, environment
loading, or process-global logging just to call a function.

## Where to change code { #where-to-change-code }

| Change | Primary location | Contract to test |
| --- | --- | --- |
| Reusable behavior | `src/template_python/core.py` or a focused new module | Values, normalization, and specific exceptions in `tests/test_core.py` or a matching new test module |
| Command, option, or user-facing error | `src/template_python/cli.py` | stdout, stderr, and exit codes in `tests/test_cli.py` |
| Environment configuration | `src/template_python/settings.py` and `.env.template` | Defaults, valid values, precedence, and rejection in `tests/test_settings.py` |
| Logging setup | `src/template_python/log.py` | Level/format validation and emitted records in `tests/test_log.py` |
| Public library API | `src/template_python/__init__.py` | Import and call the public API without initializing the CLI |
| Build or dependency change | `pyproject.toml` and `uv.lock` | Installed wheel behavior via `make package-check`; lower bounds via `make test-lowest` |

## Keep the cognitive cost small { #keep-the-cognitive-cost-small }

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
- Do not name modules after the standard library (the logging setup lives in
  `log.py`, not `logging.py`).
- Use names that reveal inputs, outputs, and responsibility. A reader should not
  need to follow several layers to understand a small operation.
- Return values or raise specific exceptions. Do not turn failures into
  success-shaped defaults, suppress errors broadly, or log secrets.
- Keep one authoritative procedure for each task. Link to it rather than
  copying commands into several documents or workflows.

For a non-obvious decision, include the problem, simplest alternative, chosen
trade-off, and verification in the PR description. A separate design document
is only useful when the rationale needs to outlive the change.

## Technology choices { #technology-choices }

The stack favors widely adopted, actively maintained tools with stable
interfaces. Versions are bounded to the current major (or minor for 0.x tools)
and resolved in `uv.lock`.

| Concern | Choice | Why |
| --- | --- | --- |
| Environment, lock, build | uv, `uv_build` | One tool for Python, venv, locking, and builds; reproducible with hashes |
| CLI | Typer (on Click) | Type-hint driven, mature Click foundation |
| Configuration | Pydantic Settings | Validated, typed environment and `.env` loading |
| Format and lint | Ruff | Formatter plus a broad rule set including bandit (`S`) security rules |
| Types | mypy (strict) with the Pydantic plugin | Reference type checker |
| Tests | pytest (strict mode), pytest-cov | De facto standard |
| Git hooks | prek (pre-commit compatible) | Reads `.pre-commit-config.yaml`; no separate Python environment |
| Dependency audit | pip-audit | PyPA-maintained; `uv audit` is still experimental |
| Secret scan | gitleaks | Hook and full-history scan |
| File and image scan | Trivy (pinned image digest) | Lock file, Dockerfile, secrets, and OS packages |
| Workflow analysis | actionlint, zizmor, CodeQL (`actions`) | Syntax, security, and data-flow checks |
| Documentation | MkDocs + Material | Stable and widely used. Material reaches end of life on 2027-05-05 (critical fixes until then); plan a migration to its successor [Zensical](https://zensical.org/docs/compatibility/mkdocs/migration/), which reads `mkdocs.yml`, before that date |

## Sources of truth { #sources-of-truth }

| Concern | Source |
| --- | --- |
| Metadata, dependencies, tool configuration | `pyproject.toml` |
| Resolved dependency and tool versions | `uv.lock` |
| uv version range | `[tool.uv] required-version` in `pyproject.toml` (also read by `setup-uv` in CI) |
| Default Python / supported versions | `.python-version` / `requires-python`, classifiers, and `.github/workflows/test.yaml` |
| Local and CI commands | `Makefile` |
| Git hooks | `.pre-commit-config.yaml` |
| Configuration schema / example overrides | `src/template_python/settings.py` / `.env.template` |
| Container behavior | `Dockerfile`, `.dockerignore`, and `compose.yml` |
| Dependency update policy | `.github/dependabot.yaml` |
| Documentation navigation | `mkdocs.yml` |

Update declarations and derived assets together. Dependency declarations change
in `pyproject.toml`; regenerate `uv.lock` with `uv lock`. CI should call Make
targets instead of maintaining another implementation of the same checks.

## Runtime rules { #runtime-rules }

- The public package must remain importable without configuring logging or
  reading environment variables.
- Core modules do not depend on Typer or settings. The CLI translates their
  values and exceptions into user-facing output and exit codes.
- `ProjectSettings` owns `PROJECT_*` environment and optional `.env` loading.
  Do not add a second dotenv loader. Commands read settings from the context
  rather than loading them again.
- Configure root logging once in the CLI callback. Library modules only obtain
  named loggers. Use `PROJECT_LOG_FORMAT=json` where logs are collected.
- Declare secrets as `SecretStr`. Typer's pretty exceptions do not show local
  variables, so tracebacks do not leak secret values.
- Expose commands through `[project.scripts]`; keep `python -m template_python`
  as a convenience path.

## Quality gate { #quality-gate }

Use the [checks by change type](../development.md#checks-by-change-type).
The Python gate checks formatting, strict types, an extended Ruff rule set
(including bandit security rules), workflow rules, and all tests with branch
coverage of at least 95%. It builds wheel and sdist, then runs the installed
wheel's CLI, module entry point, and `--version` in isolation. It does not
smoke-test the sdist installation.

Test observable contracts, including failure paths, instead of coupling tests
to internal structure. Keep stdout, stderr, exit codes, and import-time behavior
stable unless the change explicitly requires a compatibility break.

## Security and supply chain { #security-and-supply-chain }

| Layer | Control | Where |
| --- | --- | --- |
| Source | Ruff `S` rules, CodeQL (`python`, `actions`, security-extended) | `make lint`, `codeql.yaml` |
| Secrets | gitleaks hook, full-history scan, Trivy secret scanner, `detect-private-key` | Hooks, `make secret-scan`, `make security-scan` |
| Dependencies | pip-audit on every locked package (hash-verified), Trivy on `uv.lock`, Dependabot with cooldown | `make audit`, `make security-scan`, `dependabot.yaml` |
| Workflows | Actions pinned by SHA, minimal `permissions`, `persist-credentials: false`, no cache in publishing workflows, actionlint and zizmor | `.github/workflows/`, `make lint` |
| Container | Digest-pinned base and uv images, `uv sync --locked` from hashed lock, non-root user, no pip in the runtime image, hadolint, Trivy image scan | `Dockerfile`, `make ci-test-docker` |
| Release | Tag/version check, pre-release scan, SBOM and max-mode provenance, GitHub artifact attestation | `release.yaml` |
| Posture | OpenSSF Scorecard published weekly | `scorecard.yaml` |

`security.yaml` runs `make ci-test-security` on pull requests, on `main`, and
weekly, so newly disclosed vulnerabilities fail CI without a code change.

## Delivery { #delivery }

- Pull requests and supported branches run Python, security, CodeQL, and
  container validation.
- `main` publishes the bilingual documentation with GitHub Pages artifacts.
- `v*` tags run `release.yaml`, which publishes a multi-platform
  (`linux/amd64`, `linux/arm64`) image to GHCR.
- Azure Static Web Apps deployment remains manual.

The release workflow first verifies that the tag is exactly `v` followed by the
`pyproject.toml` version. It builds and scans an image with Trivy, then pushes
with an SBOM and build provenance and records a GitHub artifact attestation.
Tags follow PEP 440: `v1.2.3` publishes `1.2.3`, `1.2`, and `latest`; a
pre-release such as `v1.3.0rc1` publishes only `1.3.0rc1`. Verify an image with:

```shell
gh attestation verify oci://ghcr.io/ks6088ts/template-python:<version> --owner ks6088ts
```

GHCR uses the workflow's `GITHUB_TOKEN`. The manual site workflow requires
`AZURE_STATIC_WEB_APPS_API_TOKEN`. These credentials are not required for local
development. PyPI and Docker Hub publishing are not configured.

## Adopting the template { #adopting-the-template }

1. Rename the distribution and package: `template-python` / `template_python`
   in `pyproject.toml`, `src/`, tests, `Makefile`, `Dockerfile`, `compose.yml`,
   workflows, `mkdocs.yml`, and docs. Run `uv lock`.
2. Replace the owner in `pyproject.toml` URLs, `.github/CODEOWNERS`,
   `SECURITY.md`, badges, and `mkdocs.yml`.
3. Choose the settings prefix (`PROJECT_`) and update `.env.template` and the
   configuration reference.
4. Replace the `hello` command and `core.greeting` with real behavior and tests;
   keep `--version` and `config`.
5. Remove unused optional assets together with their dependencies, Make
   targets, workflows, and links: the notebook group and `notebooks/`, MkDocs and
   the Pages/SWA workflows, the Dev Container, or `compose.yml`.
6. In repository settings, enable private vulnerability reporting, Dependabot
   alerts, code scanning, and branch protection requiring the `test`,
   `security`, `codeql`, and `docker` checks.
7. Run `make ci-test ci-test-docs ci-test-security ci-test-docker` and tag the
   first release.
