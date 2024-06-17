FROM public.ecr.aws/docker/library/python:slim

# Install poetry
RUN pip install poetry

# Copy the poetry.lock and pyproject.toml
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install

# Copy the rest of the code
COPY . .

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0", "zephir_api:create_app()"]