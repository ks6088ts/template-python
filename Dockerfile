FROM python:3.14-slim-trixie AS build

WORKDIR /build

COPY --from=astral/uv:0.12.19 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src

RUN uv export \
    --locked \
    --no-dev \
    --no-emit-project \
    --no-hashes \
    --output-file /dist/requirements.txt \
    && uv build --wheel --out-dir /dist

FROM python:3.14-slim-trixie

ARG GIT_REVISION="0000000"
ARG GIT_TAG="0.0.0"

LABEL org.opencontainers.image.source="https://github.com/ks6088ts/template-python" \
      org.opencontainers.image.revision="${GIT_REVISION}" \
      org.opencontainers.image.version="${GIT_TAG}"

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --home-dir /app app

COPY --from=build /dist/requirements.txt /tmp/requirements.txt
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt \
    && pip install --no-cache-dir --no-deps /tmp/*.whl \
    && pip uninstall --yes pip \
    && rm /tmp/*.whl /tmp/requirements.txt

USER 10001:10001
WORKDIR /app

ENTRYPOINT ["template-python"]
CMD ["hello", "--name", "Container"]
