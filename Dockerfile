FROM alpine:latest
WORKDIR /app

RUN apk add --no-cache gcc musl-dev python3-dev poetry tini
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry install --no-root --no-dev \
    && rm -rf /root/.cache/*

COPY tl_exporter tl_exporter

ENTRYPOINT ["tini", "--"]
CMD [".venv/bin/python", "-m", "tl_exporter"]
