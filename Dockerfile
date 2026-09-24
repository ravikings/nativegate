# Repo-root MCP server image for the Glama registry (glama.ai/mcp/servers).
#
# The registry's verifier builds the repo root and runs the container over
# stdio: all it needs is a process that starts and answers MCP initialize /
# tools/list. The server is petro_api's generated FastMCP one
# (`petro_api.mcp_server`), which derives one tool per REST route from the
# router's OpenAPI schema — 11 tools, introspected and exercise-tested in
# tests/test_mcp.py. The HTTP deployment of the same app remains the
# service-own Dockerfile at services/petro_api/Dockerfile (`ngate docker`).
#
# Building this requires a Fortran compiler: the RainflowOil PVT library under
# native/ is compiled to a Python extension in the builder stage, exactly the
# recipe services/petro_api/Dockerfile uses (kept in step with it by hand —
# change there first, then here).
FROM python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a AS builder

RUN apt-get update && \
    apt-get install -y \
        build-essential=12.12 \
        gcc-14=14.2.0-19 \
        g++-14=14.2.0-19 \
        gfortran=4:14.2.0-1 \
        gfortran-14=14.2.0-19 \
        cmake=3.31.6-2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY services/petro_api/ .

# Reproducible wheel timestamps (SOURCE_DATE_EPOCH → zip epoch floor),
# reasons in services/petro_api/Dockerfile.
ENV SOURCE_DATE_EPOCH=315532800

RUN pip install --no-cache-dir build scikit-build-core numpy meson ninja

# --no-deps keeps the runtime stage on the hash-locked requirements only.
RUN pip wheel . -w /dist --no-build-isolation --no-deps

FROM python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgfortran5=14.2.0-19 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /dist /dist

COPY services/petro_api/requirements.lock ./requirements.lock

RUN pip install --no-cache-dir --require-hashes -r requirements.lock && \
    pip install --no-cache-dir --no-deps /dist/*.whl && \
    rm -rf /dist

# Non-root, same UID the generated service containers and Kubernetes
# manifests use.
RUN useradd --create-home --uid 1000 appuser
USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# stdio transport: this is what a directory/registry launches with
# `docker run -i`. The FastMCP banner is written to stderr, so stdout stays
# reserved for the JSON-RPC protocol. RainflowOil COMMON blocks are
# per-process state, which stdio mode is the natural fit for — one process,
# one session.
CMD ["python", "-c", "from petro_api.mcp_server import mcp; mcp.run()"]
