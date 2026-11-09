# Development guide

Use this guide for setup, the edit-test cycle, and recovery from failed checks.
For module boundaries and design decisions, use the
[engineering guide](architecture/README.md).
All commands below run from the repository root.

## Set up once { #set-up-once }

| Tool | When it is needed |
| --- | --- |
| [uv 0.13.x](https://docs.astral.sh/uv/getting-started/installation/) | Always; `pyproject.toml` requires `>=0.13.1,<0.14` |
| Python 3.12–3.15 | Installed by uv on demand; `.python-version` selects 3.14 |
| GNU Make | The repository's standard commands |
| Docker with a running daemon | Container checks, `secret-scan`, and `security-scan` only |

```shell
make install-deps-dev
uv run --locked template-python --help
make test
```

`uv` manages `.venv`; do not install project dependencies with a separate
`pip install` command. No activation is needed. Ruff, mypy, actionlint, zizmor,
and pip-audit are installed from `uv.lock`, so no global tools are required.

Install the Git hooks once:

```shell
make install-hooks
make hooks-check
```

Hooks run file hygiene checks, private-key and secret detection (gitleaks),
`uv lock --check`, Ruff, mypy, actionlint, and zizmor. Python tools run through
`uv run --locked`, so hooks and CI use identical versions. Hooks do not run the
tests; use `make ci-test` before pushing.

## Everyday development { #everyday-development }

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
and `make ci-test` run all tests with branch coverage and enforce at least
**95%** (the template itself is at 100%). pytest runs in strict mode and turns
warnings into errors. Do not lower the threshold or ignore warnings broadly to
make a run pass.

Tests run in an isolated temporary working directory with `PROJECT_*` variables
removed (see `tests/conftest.py`), so your shell and `.env` do not affect results.

### Checks by change type { #checks-by-change-type }

| Changed area | Focused feedback | Before submitting |
| --- | --- | --- |
| Python behavior or tests | Selected tests with `--no-cov`, `make fix`, `make type-check` | `make ci-test` |
| Dependencies or package metadata | `uv lock`, `make package-check` | `make ci-test`, `make audit`, `make test-lowest` |
| Markdown or `mkdocs.yml` | `make docs-serve` | `make ci-test-docs` |
| GitHub workflows or Dependabot | `uv run --locked actionlint`, `uv run --locked zizmor --offline .` | `make ci-test` |
| Dockerfile or Compose | `make docker-build docker-run` | `make ci-test-docker`; `docker compose up --build` if Compose changed |

Run the union of checks when a change spans areas.

| Command | What it does |
| --- | --- |
| `make help` | Lists supported Make targets |
| `make fix` | Applies Ruff fixes and formatting; review any automatic changes |
| `make lint` | Runs strict mypy, Ruff (including security rules), actionlint, and zizmor |
| `make test` | Runs pytest with branch coverage |
| `make test-lowest` | Runs tests on Python 3.12 with the lowest declared direct dependency versions |
| `make package-check` | Builds wheel and sdist, then tests the installed CLI, module entry point, and `--version` |
| `make ci-test` | Syncs dev dependencies and runs formatting, lint, tests, and package checks |
| `make audit` | Audits every locked dependency with pip-audit (hash-verified, no pip) |
| `make secret-scan` | Scans the full Git history with gitleaks (Docker) |
| `make security-scan` | Scans files with Trivy for vulnerable dependencies, misconfigurations, and secrets (Docker) |
| `make ci-test-security` | Runs `audit`, `secret-scan`, and `security-scan` |

CI runs the full gate and docs build on Python 3.14, compatibility tests on
3.12, 3.13, and 3.15, the lowest-dependency job, and hooks in separate jobs.
Security scans run on pull requests and weekly; see
[security and supply chain](architecture/README.md#security-and-supply-chain).

## Configuration { #configuration }

The CLI works with defaults. Copy `.env.template` to `.env` only if local
overrides are needed:

```shell
cp .env.template .env
```

| Variable | Default | Accepted value / effect |
| --- | --- | --- |
| `PROJECT_NAME` | `template-python` | String used in the debug startup log; does not change the greeting |
| `PROJECT_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `PROJECT_LOG_FORMAT` | `text` | `text` for humans, `json` for one JSON object per line (log collectors, containers) |

Environment variables override `.env`, which overrides defaults.
Names are case-insensitive; **values** must use the exact choices above. `.env`
is read from the working directory and unknown `PROJECT_*` entries are
rejected, so do not reuse an unrelated application's `.env`.
Keep local settings and secrets out of version control.

```shell
PROJECT_LOG_LEVEL=DEBUG uv run --locked template-python hello --name Ada
PROJECT_LOG_FORMAT=json uv run --locked template-python --verbose hello
uv run --locked template-python config
```

`config` prints the effective settings as JSON. Declare credentials as
`pydantic.SecretStr`; they are printed as `**********`.

| Global option | Effect |
| --- | --- |
| `--verbose`, `-v` | Selects debug logging after settings validation; it cannot make an invalid setting valid |
| `--version`, `-V` | Prints `template-python <version>` and exits, even if settings are invalid |
| `--help` | Shows help; running without a command also shows help (exit code 2) |

Place global options before the command (`template-python --verbose hello`).
Command output goes to stdout; logs and validation errors go to stderr. Blank
`--name` values and invalid settings exit with code **2**.

## Dependencies { #dependencies }

- Edit dependency declarations in `pyproject.toml`, run `uv lock`, and commit both
  the manifest and `uv.lock`. Do not hand-edit resolved lock entries.
- Keep lower bounds honest: `make test-lowest` installs the lowest allowed direct
  dependency versions and must pass.
- Use `make update` only for an intentional broad upgrade: it runs
  `uv lock --upgrade`, not just a sync of the current versions. Run `make audit`
  afterwards.
- Keep runtime dependencies in `project.dependencies`; keep development,
  test, docs, and notebook tools in their existing groups.
- Dependabot opens grouped weekly updates after a 7-day cooldown for Python
  packages, GitHub Actions, pre-commit hooks, Docker base images, and Dev
  Container features. Tool images in the `Makefile` and the uv version in the Dev
  Container are pinned by hand; update them together with `[tool.uv]
  required-version` when raising uv.

## Documentation { #documentation }

```shell
make docs-serve
```

Open the address printed by MkDocs (normally `http://127.0.0.1:8000`). Stop the
preview with `Ctrl+C`, then validate with:

```shell
make ci-test-docs
```

The build runs in strict mode and writes English and Japanese pages to the
ignored `site/` directory. Edit `page.md` and `page.ja.md` together. Give
headings that are linked from other pages an explicit ID such as
`## Heading { #heading }` so both languages share anchors. Add new pages to
`mkdocs.yml`, including Japanese navigation labels. Use relative links between
documentation pages. Keep onboarding in the README, procedures here, and design
rationale in the engineering guide.

## Troubleshooting { #troubleshooting }

Fix the first failing command rather than disabling checks or changing several
tools at once.

| Symptom | What to check / next action |
| --- | --- |
| `uv: command not found` | Install uv 0.13.x and ensure its directory is on `PATH`; confirm with `uv --version` |
| `Required uv version ... does not match` | Upgrade or downgrade uv into the range in `[tool.uv] required-version` (for example `uv self update`) |
| Python version is incompatible | Select a supported interpreter, for example `uv sync --locked --group dev --python 3.13` |
| Lock file needs updating | If dependencies intentionally changed, run `uv lock` and review both files; otherwise investigate manifest/lock drift rather than removing `--locked` |
| `make audit` reports a vulnerability | Upgrade the package (`uv lock --upgrade-package <name>`) and rerun; only ignore an ID with a documented reason |
| `make test-lowest` fails | Raise the lower bound in `pyproject.toml` to the first version that works, then `uv lock` |
| `Invalid configuration` / exit code 2 | Check `PROJECT_*` variables and the working directory's `.env`; use an accepted value |
| A selected test run fails coverage | Use `--no-cov` for the subset, then run `make test` for the actual coverage gate |
| Docker cannot connect to the daemon | Start Docker before retrying; it is only needed for container and scan targets |
| A new page is absent or a link is broken | Check `mkdocs.yml`, both language files, heading IDs, and the link target, then rebuild |

When requesting help, include the exact command, first failure, OS, Python/uv
versions, and relevant change. Redact secrets and private configuration.
