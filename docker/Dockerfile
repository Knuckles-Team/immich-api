# syntax=docker/dockerfile:1
# MCP serving image; --target mcp and the default target are equivalent.
FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS builder-base
COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_HTTP_TIMEOUT=3600
# A few transitive deps ship no manylinux wheel and build from sdist, needing a C++
# toolchain. Install it in the builder only — final stages copy just /usr/local.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Build the connector from this checkout, including generated runtime data.
# Copy only the package and its wheel metadata, not credentials or local tooling.
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY immich_api/ ./immich_api/

# MCP serving dependency closure (including SDK graph client).
FROM builder-base AS builder-mcp
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --break-system-packages --prerelease=allow ".[mcp]"

FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS runtime-base
ARG HOST=127.0.0.1
ARG PORT=8000
ARG TRANSPORT="stdio"
ARG AUTH_TYPE="none"
ENV HOST=${HOST} \
    PORT=${PORT} \
    TRANSPORT=${TRANSPORT} \
    AUTH_TYPE=${AUTH_TYPE} \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:/usr/local/bin:${PATH}" \
    UV_HTTP_TIMEOUT=3600 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# MCP serving image.
FROM runtime-base AS mcp
COPY --from=builder-mcp /usr/local /usr/local
CMD ["immich-mcp"]

FROM mcp AS default
