FROM python:3.10-slim

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN apt-get -y update &&\
    pip install poetry==1.1.13 && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    pip install --no-cache-dir --upgrade -r /tmp/requirements.txt &&\
    apt-get install -y ffmpeg

WORKDIR /bot

COPY ./app /bot/app

COPY ./alembic.ini /bot/

EXPOSE 2280
