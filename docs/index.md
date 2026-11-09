# template-python

A typed Python 3.12+ CLI template with a production-grade toolchain. Start with
the runnable example, then read only the guide needed for your task. Containers,
notebooks, and deployment are optional, not prerequisites.

## Run the example

Install [uv 0.13.x](https://docs.astral.sh/uv/getting-started/installation/)
and GNU Make. uv installs Python 3.14 from `.python-version`. Run these commands
from the repository root:

```shell
make install-deps-dev
uv run --locked template-python hello --name Ada
make test
```

The CLI prints:

```text
Hello, Ada!
```

No `.env` file or virtual environment activation is required. Python 3.14 is the
full CI baseline; 3.12, 3.13, and 3.15 also have compatibility tests, and the
lowest declared dependency versions are tested on 3.12.

## Find the next step

| Task | Guide |
| --- | --- |
| Set up development, change code, and select checks | [Development](development.md) |
| Find the right module or make a design decision | [Architecture and engineering](architecture/README.md) |
| Set environment variables or understand CLI errors | [Configuration](development.md#configuration) |
| Understand scanners, CI, and releases | [Security and supply chain](architecture/README.md#security-and-supply-chain) |
| Recover from a failed command | [Troubleshooting](development.md#troubleshooting) |
| Rename the template or remove unused assets | [Adopting the template](architecture/README.md#adopting-the-template) |
| Preview and validate these pages | [Documentation workflow](development.md#documentation) |

## What to remember

- Reusable behavior belongs in the core; the CLI handles settings, logging,
  output, and exit codes.
- `Makefile` is the command reference; use `make help` rather than memorizing
  tool flags. CI calls the same targets.
- `pyproject.toml` declares dependencies and tool settings; `uv.lock` records
  resolved versions, including the linters used by Git hooks.
- Keep English and Japanese pages aligned. Do not duplicate detailed procedures
  in the README; link to the relevant guide instead.
