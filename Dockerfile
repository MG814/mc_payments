FROM python:3.13
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=False
WORKDIR /app
COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN pip install poetry
RUN poetry install

COPY . /app