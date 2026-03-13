# zephir_api2

The Zephir Item API provides item-level MARC metadata records for all items submitted to HathiTrust.

See [API.md](API.md) for full endpoint documentation.

## Workflow

This repository uses [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow). The `main` branch is always assumed to be tested and ready for deployment to production. Ensure all changes are adequately tested _before_ merging into `main`.

## Getting Started

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) — it manages both Python and project dependencies:

```sh
brew install uv
```

### Local Development

1. Install dependencies

    ```sh
    uv sync
    ```

2. Install git hooks

    ```sh
    git config core.hooksPath .githooks
    ```

    This enables the pre-commit hook that runs ruff and vulture before each commit.

3. Set required environment variables

    Copy `env.template` to `.env` and update the `DATABASE_URI` variable. See [Database configuration](#database-configuration) below.

4. Run the app

    ```sh
    uv run python -m gunicorn -c gunicorn_config.py
    ```

    The API will be available at `http://localhost:8000/api/`.

### Running tests

```sh
uv run pytest tests
```

Tests use a bundled SQLite fixture (`tests/test_zephir_api/`) and do not require a live database connection.

### Linting, etc.

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

## CI (Continuous Integration)

CI runs on AWS CodeBuild in the `cdl-d2d-dev` account. Every pull request triggers a build that runs tests, linting, and security checks, and reports a check status with a link to the build log back to GitHub.

The job configuration lives in [`buildspec.yml`](buildspec.yml).

### First-time setup

The CodeBuild project is managed by Sceptre. Note that the GitHub connection is created and activated manually before deploying.

### Test results

Build status is automatically reported to GitHub on every PR. Test results are published to the CodeBuild **Test reports** panel (JUnit XML).

## Deploying to AWS

### Deploy latest

1. Set the AWS profile you will use to run deployment commands (typically `cdl-d2d-dev` or `cdl-d2d-prod`)

    `export AWS_PROFILE=<profile_for_env>`

2. Login to AWS with the appropriate profile (Credentials expire after 12 hours.)

    `aws sso login --profile <profile_for_env>`

3. Build a fresh Docker image from the latest code and push it to ECR

    The image will automatically be tagged with `latest` and the current commit hash.

    `uv run sh deployment/scripts/ecr_push.sh <env>`

4. Deploy! Only resources which have changed will be redeployed. To deploy the latest container you should provide a unique image tag (i.e. the commit hash). Using `latest` will not trigger a redeploy if the previously deployment used the same tag.

    `uv run sh deployment/scripts/deploy.sh <env> <image_tag>`

### Tear down

**CAUTION! CAUTION! This command will destroy all related AWS resources**

`uv run sh deployment/scripts/destroy.sh <env>`.
