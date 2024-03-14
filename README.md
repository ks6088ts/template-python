[![test](https://github.com/ks6088ts/template-python/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ks6088ts/template-python/actions/workflows/test.yml?query=branch%3Amain)

# template-python

This is a template repository for a Python

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [GNU Make](https://www.gnu.org/software/make/)

## Development instructions

### Local development

Use Makefile to run the project locally.

```shell
# help
make

# install dependencies for development
make install-deps-dev

# run tests
make test

# run CI tests
make ci-test
```
