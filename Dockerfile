FROM python:3.12-slim-bookworm

LABEL authors="denisdoncu"

WORKDIR /language_learning_app

RUN pip install poetry==2.1.3

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY . .

EXPOSE 8000

