FROM python:3.11-slim-bullseye

WORKDIR /app
RUN useradd --create-home appuser

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV PATH=/home/appuser/.local/bin:$PATH

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

USER appuser

RUN pip install poetry
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install

COPY ./candle ./candle

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
