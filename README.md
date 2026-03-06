# zephir_api2
 
![CI](https://github.com/cdlib/zephir-api2/actions/workflows/ci.yml/badge.svg)

The Zephir Item API provides item-level MARC metadata records for all items submitted to HathiTrust.
See [API.md](API.md) for full endpoint documentation.

## Getting Started

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) — it manages both Python and project dependencies:

```sh
brew install uv
```

### Local Development

**Install dependencies:**

```sh
uv sync
```

**Set required environment variables** (see [Database configuration](#database-configuration) below), then **run the app:**

```sh
export FLASK_ENV=development
export APP_PORT=8000
export LOG_LEVEL=INFO
export DATABASE_URI=mysql+mysqlconnector://user:pass@host/dbname

uv run python -m gunicorn -c gunicorn_config.py
```

The API will be available at `http://localhost:8000`.

**Run tests:**

```sh
uv run pytest tests
```

Tests use a bundled SQLite fixture (`tests/test_zephir_api/`) and do not require a live database connection.

**Run linting and analysis tools:**

```sh
uv run ruff check .
uv run bandit -r app
uv run vulture . --min-confidence 70 --exclude .venv
uv run pytest --cov=app --cov-report=term-missing
```

### Docker

The Dockerfile has three useful targets:

| Target | What it does |
|---|---|
| `test` | Installs all deps, copies source, runs `pytest tests` on start |
| `test-minor-update` | Same as `test` but upgrades deps to latest compatible versions first |
| `production` | Installs prod deps only, starts Gunicorn on start |

**Run a single target directly:**

```sh
# Run the test suite
docker run $(docker build -q --target test .)

# Build and run the production image
docker run -p 8000:8000 \
  -e FLASK_ENV=production \
  -e APP_PORT=8000 \
  -e LOG_LEVEL=INFO \
  -e DATABASE_URI=mysql+mysqlconnector://user:pass@host/dbname \
  $(docker build -q --target production .)
```

**Run with Docker Compose:**

1. Create a `.env` file in the project root:

   ```
   FLASK_ENV=development
   APP_PORT=8000
   LOG_LEVEL=INFO
   DATABASE_URI=mysql+mysqlconnector://user:pass@host/dbname
   ```

2. Start the stack:

   ```sh
   docker compose up
   ```

   The API will be available at `http://localhost:8000` once tests pass.

---

## Database Configuration

The app resolves the database connection from environment variables in priority order:

| Variable | When to use |
|---|---|
| `DATABASE_URI` | Full SQLAlchemy URI — simplest for local dev |
| `DATABASE_CREDENTIALS_SECRET_NAME` + AWS vars | Pull credentials from AWS Secrets Manager |
| `DB_USERNAME` + `DB_PASSWORD` + `DB_HOST` + `DB_DATABASE` | Individual credential env vars |

---

## Dependency Management

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

| Command | Purpose |
|---|---|
| `uv sync` | Install all dependencies (prod + dev) |
| `uv sync --no-dev` | Install production dependencies only |
| `uv add <package>` | Add a new runtime dependency |
| `uv add --dev <package>` | Add a new dev dependency |
| `uv lock --upgrade` | Update all dependencies within version constraints |
| `uv tree --outdated` | List dependencies with available updates |
