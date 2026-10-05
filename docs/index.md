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
template_python.core -> template_python.loggers -> template_python.settings
```

Higher layers may import lower layers, including skipping a layer
(`core` may import `settings` directly). Lower layers must not import higher
layers, directly or indirectly through other modules. Child modules such as
`settings.project` and imports under `if TYPE_CHECKING:` are also checked.

`make lint` and `make ci-test` include this check, and violations fail the
existing Python 3.13 CI quality gate. The contract covers `template_python`;
scripts, tests, and external-library dependencies have no additional constraints.
Git hooks and deployment workflows are unchanged.

The contract is not exhaustive: new top-level modules do not have to be assigned
to a layer, but reverse dependencies between the existing layers through those
modules are still checked. To constrain a new layer, update
`tool.importlinter.contracts` in `pyproject.toml` in highest-to-lowest order.
