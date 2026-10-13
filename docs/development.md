# Development guide

Use this guide for setup, the edit-test cycle, and recovery from failed checks.
For module boundaries and design decisions, use the
[engineering guide](architecture/README.md).
All commands below run from the repository root.

## Set up once

| Tool | When it is needed |
| --- | --- |
| Python 3.12+ | Package and tests; prefer 3.13 to match the full CI job |
| [uv 0.12.19](https://docs.astral.sh/uv/getting-started/installation/) | Locked dependencies and command execution |
| GNU Make | The repository's standard commands |
| [actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md) | `make lint` and `make ci-test`; CI uses 1.7.12 |
| Docker with a running daemon | Container commands only |

```shell
make install-deps-dev
uv run --locked template-python --help
make test
```

`uv` manages `.venv`; do not install project dependencies with a separate
`pip install` command. No activation is needed. The actionlint reminder printed
by `make install-deps-dev` does not prevent Python tests from running.

Optional Git hooks:

```shell
make install-hooks
make hooks-check
```

Hooks check YAML, whitespace, and Ruff rules. They do not replace type checking,
tests, or the full quality gate.

## Everyday development

1. Find the module and its test using the
   [change map](architecture/README.md#where-to-change-code).
2. Define the expected output and failure behavior in a focused test.
3. Implement the smallest change that satisfies that contract.
4. Run focused tests, then formatting and the checks for the changed area.
5. Update the relevant English and Japanese documentation if behavior changes.

For a greeting or CLI change, start with:

```shell
uv run --locked pytest --no-cov tests/test_core.py tests/test_cli.py
make fix
make ci-test
```

`--no-cov` is only for the focused feedback loop: measuring a subset against the
whole-package coverage threshold would give misleading failures. `make test`
and `make ci-test` run all tests with branch coverage and enforce **95%** minimum
coverage. Do not lower the threshold to make a focused run pass.

### Checks by change type

| Changed area | Focused feedback | Before submitting |
| --- | --- | --- |
| Python behavior or tests | Selected tests with `--no-cov`, `make fix`, `make type-check` | `make ci-test` |
| Dependencies or package metadata | `uv lock`, `make package-check` | `make ci-test`; docs/container checks if affected |
| Markdown or `mkdocs.yml` | `make docs-serve` | `make ci-test-docs` |
| GitHub workflows | `actionlint` | `make ci-test` and the checks invoked by the changed workflow |
| Dockerfile or Compose | `make docker-build docker-run` | `make ci-test-docker`; `docker compose up --build` if Compose changed |

Run the union of checks when a change spans areas. Documentation-only changes
do not need the Python or container gate.

Useful commands, without a new workflow to memorize:

| Command | What it does |
| --- | --- |
| `make help` | Lists supported Make targets |
| `make fix` | Applies Ruff fixes and formatting; review any automatic changes |
| `make lint` | Runs strict mypy, Ruff, actionlint, and offline zizmor |
| `make test` | Runs pytest with branch coverage |
| `make package-check` | Builds wheel and sdist, then tests the wheel's installed CLI and module entry point in isolation |
| `make ci-test` | Syncs dev dependencies and runs formatting, lint, tests, and package checks |

CI runs the full gate and docs build on Python 3.13, compatibility tests on
3.12 and 3.14, and hooks in a separate job.

## Configuration

The CLI works with defaults. Copy `.env.template` to `.env` only if local
overrides are needed:

```shell
cp .env.template .env
```

| Variable | Default | Accepted value / effect |
| --- | --- | --- |
| `PROJECT_NAME` | `template-python` | String used in the debug startup log; does not change the greeting |
| `PROJECT_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |

Environment variables override `.env`, which overrides defaults.
Names are case-insensitive; log-level **values** must use the uppercase choices
above. `.env` is read from the working directory and unknown entries are
rejected, so do not reuse an unrelated application's `.env`.
Keep local settings and secrets out of version control.

```shell
PROJECT_LOG_LEVEL=DEBUG uv run --locked template-python hello --name Ada
uv run --locked template-python --verbose hello --name Ada
```

`--verbose` is a global option: place it before `hello`. It selects debug logging
after settings validation; it cannot make an invalid setting valid.
Successful greeting output goes to stdout; logs and validation errors go to
stderr. Blank `--name` values and invalid settings exit with code **2**.

## Dependencies

- Edit dependency declarations in `pyproject.toml`, run `uv lock`, and commit both
  the manifest and `uv.lock`. Do not hand-edit resolved lock entries.
- Use `make update` only for an intentional broad upgrade: it runs
  `uv lock --upgrade`, not just a sync of the current versions.
- Keep runtime dependencies in `project.dependencies`; keep development,
  test, docs, and notebook tools in their existing groups.
- Existing commands select and sync their dependency groups. Docs and notebook
  commands use `--no-dev`; a later dev command restores the dev group as needed.

## Documentation

```shell
make docs-serve
```

Open the address printed by MkDocs (normally `http://127.0.0.1:8000`). Stop the
preview with `Ctrl+C`, then validate with:

```shell
make ci-test-docs
```

The build writes English and Japanese pages to the ignored `site/` directory.
Edit `page.md` and `page.ja.md` together. Add new pages to `mkdocs.yml`, including
Japanese navigation labels. Use relative links between documentation pages.
Keep onboarding in the README, procedures here, and design rationale in the
engineering guide.

## Troubleshooting

Fix the first failing command rather than disabling checks or changing several
tools at once.

| Symptom | What to check / next action |
| --- | --- |
| `uv: command not found` | Install the pinned uv version and ensure its directory is on `PATH`; confirm with `uv --version` |
| Python version is incompatible | Select a supported interpreter, for example `uv sync --locked --group dev --python 3.13` |
| `actionlint: command not found` during lint/CI | Install actionlint and confirm `actionlint --version`; `make test` remains available for focused work |
| Lock file needs updating | If dependencies intentionally changed, run `uv lock` and review both files; otherwise investigate manifest/lock drift rather than removing `--locked` |
| `Invalid configuration` / exit code 2 | Check `PROJECT_*` variables and the working directory's `.env`; use an accepted uppercase log level |
| A selected test run fails coverage | Use `--no-cov` for the subset, then run `make test` for the actual coverage gate |
| Docker cannot connect to the daemon | Start Docker before retrying; container tooling is not needed for Python-only work |
| A new page is absent or a link is broken | Check `mkdocs.yml`, both language files, and the link target, then rebuild both languages |

When requesting help, include the exact command, first failure, OS, Python/uv
versions, and relevant change. Redact secrets and private configuration.
