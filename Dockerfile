FROM python:3.11.8-slim-bookworm

ARG GIT_REVISION="0000000"
ARG GIT_TAG="x.x.x"

WORKDIR /app
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install poetry: https://python-poetry.org/docs/#installing-with-the-official-installer
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install dependencies
COPY pyproject.toml poetry.lock Makefile /app/
RUN poetry config virtualenvs.create false && make install-deps
COPY . .

CMD ["python", "main.py"]
