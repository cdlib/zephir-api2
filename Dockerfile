FROM python:3.13-slim-bullseye AS base
# # Allowing the argumenets to be read into the dockerfile. Ex:  .env > compose.yml > Dockerfile
# ARG UID=1000
# ARG GID=1000

# # Create the user and usergroup
# RUN groupadd -g ${GID} -o app
# RUN useradd -m -d /app -u ${UID} -g ${GID} -o -s /bin/bash app

# Set the working directory to /app
WORKDIR /app

# Both build and development need uv, so it is its own step.
FROM base AS uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Use this page as a reference for python environment variables:
# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED Ensure
# the stdout and stderr streams are sent straight to terminal, then you can see
# the output of your application
ENV PYTHONUNBUFFERED=1 \
    # Compile Python bytecode for faster startup
    UV_COMPILE_BYTECODE=1 \
    # Use copy mode (required in Docker; hardlinks don't work across layers)
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv_cache

FROM uv AS build
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen --no-install-project && rm -rf ${UV_CACHE_DIR}

FROM build AS test
# Install dev dependencies
RUN uv sync --frozen --no-install-project && rm -rf ${UV_CACHE_DIR}
COPY . .

# Run tests
# USER app
RUN uv run pytest tests

FROM build AS test-minor-update
# Install dev dependencies and update to latest compatible versions
RUN uv lock --upgrade && uv sync --no-install-project && rm -rf ${UV_CACHE_DIR}
COPY . .
# Run tests
# USER app
RUN uv run pytest tests


# FROM base AS production
# RUN mkdir -p /venv && chown ${UID}:${GID} /venv

# By adding /venv/bin to the PATH, the dependencies in the virtual environment
# are used
# ENV VIRTUAL_ENV=/venv \
#     PATH="/venv/bin:$PATH"

# COPY --chown=${UID}:${GID} . /app
# COPY --chown=${UID}:${GID} --from=build "/app/.venv" ${VIRTUAL_ENV}
COPY . .

# Switch to the app user
# USER app