# template-python

A typed Python 3.12+ package and CLI template. Start with the runnable example,
then read only the guide needed for your task. Containers, notebooks, and
deployment are optional, not prerequisites.

## Run the example

Install [uv 0.12.19](https://docs.astral.sh/uv/getting-started/installation/),
Python 3.12+, and GNU Make. Run these commands from the repository root:

```shell
make install-deps-dev
uv run --locked template-python hello --name Ada
make test
```

The CLI prints:

```text
Hello, Ada!
```

No `.env` file or virtual environment activation is required. Python 3.13 is the
full CI baseline; 3.12 and 3.14 also have compatibility tests.

## Find the next step

| Task | Guide |
| --- | --- |
| Set up development, change code, and select checks | [Development](development.md) |
| Find the right module or make a design decision | [Architecture and engineering](architecture/README.md) |
| Set environment variables or understand CLI errors | [Configuration](development.md#configuration) |
| Recover from a failed command | [Troubleshooting](development.md#troubleshooting) |
| Rename the template or remove unused assets | [Adopting the template](architecture/README.md#adopting-the-template) |
| Preview and validate these pages | [Documentation workflow](development.md#documentation) |

## What to remember

- Reusable behavior belongs in the core; the CLI handles settings, logging,
  output, and exit codes.
- `Makefile` is the command reference; use `make help` rather than memorizing
  tool flags.
- `pyproject.toml` declares dependencies; `uv.lock` records resolved versions.
- Keep English and Japanese pages aligned. Do not duplicate detailed procedures
  in the README; link to the relevant guide instead.
