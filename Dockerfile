ARG IMAGE_TAG=3.13-slim-bullseye

FROM python:${IMAGE_TAG} AS base
# Allowing the argumenets to be read into the dockerfile. Ex:  .env > compose.yml > Dockerfile
ARG UID=1000
ARG GID=1000

# Create the user and usergroup
RUN groupadd -g ${GID} -o app
RUN useradd -m -d /app -u ${UID} -g ${GID} -o -s /bin/bash app

# Set the working directory to /app
WORKDIR /app

# Both build and development need poetry, so it is its own step.
FROM base AS poetry
RUN pip install poetry

# Use this page as a reference for python and poetry environment variables:
# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED Ensure
# the stdout and stderr streams are sent straight to terminal, then you can see
# the output of your application
ENV PYTHONUNBUFFERED=1\
    # Avoid the generation of .pyc files during package install
    # Disable pip's cache, then reduce the size of the image
    PIP_NO_CACHE_DIR=off \
    # Save runtime because it is not look for updating pip version
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Disable poetry interaction
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

FROM poetry AS build
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev && rm -rf ${POETRY_CACHE_DIR};

# FROM poetry AS build-minor-update
# # Install minor version updates in the absence of poetry.lock file
# COPY pyproject.toml poetry.lock ./
# RUN poetry install --no-root --without dev && rm -rf ${POETRY_CACHE_DIR};

FROM build AS test
# Install dev dependencies
RUN poetry install --only dev --no-root && rm -rf ${POETRY_CACHE_DIR};
COPY . .
# Run tests
USER app
RUN poetry run pytest tests

FROM build AS test-minor-update
# Install dev dependencies
RUN poetry install --only dev --no-root && rm -rf ${POETRY_CACHE_DIR};
RUN poetry update
COPY . .
# Run tests
USER app
RUN poetry run pytest tests


FROM base AS production
RUN mkdir -p /venv && chown ${UID}:${GID} /venv

# By adding /venv/bin to the PATH, the dependencies in the virtual environment
# are used
ENV VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH"

COPY --chown=${UID}:${GID} . /app
COPY --chown=${UID}:${GID} --from=build "/app/.venv" ${VIRTUAL_ENV}
COPY . .

# Switch to the app user
USER app