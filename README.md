[![test](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/test.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/docker.yaml?query=branch%3Amain)
[![docker-release](https://github.com/ks6088ts/template-python/actions/workflows/docker-release.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/docker-release.yaml)
[![ghcr-release](https://github.com/ks6088ts/template-python/actions/workflows/ghcr-release.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/ghcr-release.yaml)
[![docs](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml/badge.svg)](https://github.com/ks6088ts/template-python/actions/workflows/github-pages.yaml)

# template-python

This is a template repository for Python

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/) (CI tests 3.10 through 3.14)
- [uv 0.12.19](https://docs.astral.sh/uv/getting-started/installation/)
- [GNU Make](https://www.gnu.org/software/make/)
- [actionlint](https://github.com/rhysd/actionlint) for local lint/CI checks (CI uses v1.7.12)
- [Docker](https://docs.docker.com/get-docker/) for the Docker targets

## Development instructions

### Local development

Use Makefile to run the project locally.

```shell
# help
make

# install dependencies for development
make install-deps-dev

# check all configured hooks
make hooks-check

# check types with mypy
make type-check

# check dependency directions with import-linter
make import-lint

# run tests
make test

# run CI tests
make ci-test

# build the English and Japanese documentation
make ci-test-docs

# launch JupyterLab
make jupyterlab
```

`make install-deps-dev` installs all development groups and installs the
[prek](https://prek.j178.dev/) Git hook, replacing a previously installed
pre-commit hook. CI uses a smaller dependency set without JupyterLab; the
notebook group remains available through `make jupyterlab`.
`make type-check` runs mypy in strict mode on `template_python/`, `scripts/`,
and `tests/`, using Python 3.10 as the target version and the Pydantic plugin.
Notebooks are not included in this mypy check. `make lint` includes this target
alongside the existing ty and pyrefly checks, so `make ci-test` also checks types
and fails on type errors. CI runs these quality checks on Python 3.13; the other
Python versions run compatibility tests only. Git hooks and deployment workflows
are unchanged, and this does not add a pre-deployment gate.
`make lint` also runs an offline [zizmor](https://zizmor.sh/) check that blocks
high-severity GitHub Actions configuration findings. Run
`uv run --locked zizmor --offline .` to review lower-severity findings as well.

### Dependency direction checks

`make import-lint` runs [import-linter](https://import-linter.readthedocs.io/)
using the layers contract in `pyproject.toml`:

```text
scripts (applications) -> template_python (library)
```

Modules under `scripts/` are applications that may import the
`template_python` library. No module in `template_python` may import `scripts`
or its child modules, directly or indirectly. This boundary also applies to
new modules added under either directory.

Imports under `if TYPE_CHECKING:` are also checked. There are no dependency
direction constraints between modules within the library.

The check is included in `make lint` and `make ci-test`, so dependency violations
fail the existing Python 3.13 CI quality gate. It analyzes both `scripts` and
`template_python`; tests and external-library dependencies have no additional
constraints. Git hooks and deployment workflows are unchanged.

### Docker development

```shell
# build docker image
make docker-build

# run docker container
make docker-run

# run CI tests in docker container
make ci-test-docker
```

The Docker CI target lints, builds, scans, and runs the image. The Trivy scan
currently reports vulnerabilities without failing the build; review its
findings before enabling a blocking severity threshold.

The documentation uses Material for MkDocs with `mkdocs-static-i18n` to publish
both languages. A switch to Zensical requires equivalent multilingual output;
unsupported MkDocs plugins are not run by Zensical.

## Deployment instructions

### Docker Hub

To publish the docker image to Docker Hub, you need to [create access token](https://app.docker.com/settings/personal-access-tokens/create) and set the following secrets in the repository settings.

```shell
gh secret set DOCKERHUB_USERNAME --body $DOCKERHUB_USERNAME
gh secret set DOCKERHUB_TOKEN --body $DOCKERHUB_TOKEN
```

### Azure Static Web Apps

```shell
RESOURCE_GROUP_NAME=your-resource-group-name
SWA_NAME=your-static-web-app-name

# Create a static app
az staticwebapp create --name $SWA_NAME --resource-group $RESOURCE_GROUP_NAME

# Retrieve the API key
AZURE_STATIC_WEB_APPS_API_TOKEN=$(az staticwebapp secrets list --name $SWA_NAME --query "properties.apiKey" -o tsv)

# Set the API key as a GitHub secret
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body $AZURE_STATIC_WEB_APPS_API_TOKEN
```

Refer to the following links for more information:

- [Deploying to Azure Static Web App](https://docs.github.com/en/actions/use-cases-and-examples/deploying/deploying-to-azure-static-web-app)
- [Create a static web app: `az staticwebapp create`](https://learn.microsoft.com/en-us/cli/azure/staticwebapp?view=azure-cli-latest#az-staticwebapp-create)
