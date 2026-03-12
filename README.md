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

Copy `env.template` to `.env` and update the `DATABASE_URI` variable.

```sh
uv run python -m gunicorn -c gunicorn_config.py
```

The API will be available at `http://localhost:8000/api/`.

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
  -e DATABASE_URI=mysql+mysqlconnector://user:pass@host/dbname \
  $(docker build -q --target production .)
```

**Run with Docker Compose:**

Docker Compose will automatically bootstrap a MySQL instance with test data from `tests/sample_data.csv`.

```sh
docker compose up
```

The API will be available at `http://localhost:8000/api/` once the MySQL service has finished bootstrapping.

---

## Database Configuration

The app resolves the database connection from environment variables in priority order:

| Variable | When to use |
|---|---|
| `DATABASE_URI` | Full SQLAlchemy URI — simplest for local dev |
| `DATABASE_CREDENTIALS_SECRET_NAME` + AWS vars | Pull credentials from AWS Secrets Manager |
| `DB_USERNAME` + `DB_PASSWORD` + `DB_HOST` + `DB_DATABASE` | Individual credential env vars |

---

## Deploying to AWS

### Deploy latest

1. Set the AWS profile you will use to run deployment commands (typically `cdl-d2d-dev` or `cdl-d2d-prod`)

    `export AWS_PROFILE=<profile_for_env>`

2. Login to AWS with the appropriate profile (Credentials expire after 12 hours.)

    `aws sso login --profile <profile_for_env>`

3. Build a fresh ECR image from the latest code and push to ECR

    Valid environments are `dev`, `stg`, and `prd`.

    `uv run --directory deployment sh scripts/ecr_push.sh <env>`

4. Deploy! Only resources which have changed will be redeployed. To deploy the latest container you must provide an unique image tag (i.e. the SHA). Using `latest` will not cause a redeploy if the previously deployed image was also on that tag.

    `uv run --directory deployment sh scripts/deploy.sh <env> <image_tag>`

### Tear down

**CAUTION! CAUTION! This command will destroy all related AWS resources**

`uv run --directory deployment sh scripts/destroy.sh <env>`.
