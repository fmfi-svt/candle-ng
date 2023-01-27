FROM python:3.10-slim-bullseye

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

COPY ./requirements ./requirements
RUN pip install -r requirements/requirements.txt

COPY ./candle ./candle

CMD ["flask", "run", "--host=0.0.0.0"]
