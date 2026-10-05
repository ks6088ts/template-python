# template-python

This repository is a template repository for Python projects.

## Dependency direction checks

Install the development dependencies and run the architecture check:

```shell
make install-deps-dev
make import-lint
```

[import-linter](https://import-linter.readthedocs.io/) uses the layers contract
in `pyproject.toml` to enforce the following dependency direction:

```text
scripts (applications) -> template_python (library)
```

Modules under `scripts/` are applications that may import the
`template_python` library. No module in `template_python` may import `scripts`
or its child modules, directly or indirectly. This boundary also applies to
new modules added under either directory.

Imports under `if TYPE_CHECKING:` are also checked. There are no dependency
direction constraints between modules within the library.

`make lint` and `make ci-test` include this check, and violations fail the
existing Python 3.13 CI quality gate. The contract covers both `scripts` and
`template_python`; tests and external-library dependencies have no additional
constraints. Git hooks and deployment workflows are unchanged.
