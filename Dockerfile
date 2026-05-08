# syntax=docker/dockerfile:1.7
# ---------------------------------------------------------------------------
# Build stage: install runtime dependencies into a self-contained virtualenv.
# Uses the official uv image so we always get a recent, signed release of uv.
# ---------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:0.7.12-python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install dependencies first to maximise Docker layer caching.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy the project sources and install the project itself.
COPY template_python ./template_python
COPY README.md LICENSE ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---------------------------------------------------------------------------
# Runtime stage: minimal Python image, non-root user, no build toolchain.
# ---------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS runtime

ARG GIT_REVISION="0000000"
ARG GIT_TAG="0.0.0"

# OCI image labels (https://github.com/opencontainers/image-spec/blob/main/annotations.md)
LABEL org.opencontainers.image.title="template-python" \
      org.opencontainers.image.description="A GitHub template repository for Python" \
      org.opencontainers.image.source="https://github.com/ks6088ts/template-python" \
      org.opencontainers.image.url="https://github.com/ks6088ts/template-python" \
      org.opencontainers.image.documentation="https://ks6088ts.github.io/template-python" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.revision="${GIT_REVISION}" \
      org.opencontainers.image.version="${GIT_TAG}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/app/.venv/bin:${PATH}"

# Create an unprivileged user (UID 10001) and a writable working directory.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app \
    && mkdir -p /app \
    && chown -R app:app /app

WORKDIR /app

# Copy the virtualenv built in the previous stage.
COPY --from=builder --chown=app:app /app/.venv /app/.venv

USER app

# Lightweight liveness probe: ensures the runtime can import the package.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import template_python"]

CMD ["python", "-m", "template_python.core"]
