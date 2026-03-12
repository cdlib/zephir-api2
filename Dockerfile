ARG IMAGE_TAG=3.13-slim-trixie

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
# Production stage
#
FROM python:${IMAGE_TAG} AS production

# Copy uv binary for runtime
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv

# Create an unprivileged user and group to run the application
RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid app --no-create-home app

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    # Deps are pre-installed in the venv; no cache needed at runtime
    UV_NO_CACHE=1

# Copy the virtualenv from the deps stage with correct ownership
COPY --from=deps --chown=app:app /app/.venv /app/.venv

# Copy application source with correct ownership
COPY --chown=app:app . .

# Switch to the unprivileged user before starting the process
USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD /app/healthcheck.sh

CMD ["uv", "run", "python", "-m", "gunicorn", "-c", "gunicorn_config.py"]