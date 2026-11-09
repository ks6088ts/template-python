# syntax=docker/dockerfile:1

# Build a virtual environment from uv.lock; hashes in the lock file are verified.
FROM python:3.14-slim-trixie@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f AS build

COPY --from=astral/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /src

# Install dependencies first so this layer is reused until the lock file changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.14-slim-trixie@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f

ARG GIT_REVISION="0000000"
ARG GIT_TAG="0.0.0"

LABEL org.opencontainers.image.title="template-python" \
      org.opencontainers.image.description="A minimal, typed Python CLI template" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/ks6088ts/template-python" \
      org.opencontainers.image.revision="${GIT_REVISION}" \
      org.opencontainers.image.version="${GIT_TAG}"

# Apply Debian security fixes published after the base image was built, and remove pip
# (and its vendored libraries) because the runtime never installs packages.
RUN apt-get update \
    && apt-get upgrade --yes --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip uninstall --yes --root-user-action=ignore pip \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --no-create-home --home-dir /app app

COPY --from=build --chown=root:root /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER 10001:10001
WORKDIR /app

ENTRYPOINT ["template-python"]
CMD ["hello", "--name", "Container"]
