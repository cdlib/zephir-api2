ARG IMAGE_TAG=3.13-slim-bullseye

#
# Python dependencies stage
#
FROM python:${IMAGE_TAG} AS deps

# Copy uv binary for dependency management
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    # Compile Python bytecode for faster startup
    UV_COMPILE_BYTECODE=1 \
    # Use copy mode (required in Docker; hardlinks don't work across layers)
    UV_LINK_MODE=copy

# Install production dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

#
# Test stage
#
FROM deps AS test

# Install dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY . .

CMD ["uv", "run", "pytest", "tests"]

#
# Test stage (with minor version updates)
#
FROM deps AS test-minor-update

# Update to latest compatible versions and install dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock --upgrade && uv sync --no-install-project

COPY . .

CMD ["uv", "run", "pytest", "tests"]

#
# Production stage
#
FROM python:${IMAGE_TAG} AS production

# Copy uv binary for runtime
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copy the virtualenv from the deps stage
COPY --from=deps /app/.venv /app/.venv

# Copy application source
COPY . .

CMD ["uv", "run", "python", "-m", "gunicorn", "-c", "gunicorn_config.py"]