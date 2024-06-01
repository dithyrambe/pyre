FROM python:3.11-slim AS builder

RUN apt update && apt install -y curl
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:$PATH"

COPY . .
RUN poetry build --format wheel

FROM python:3.11-slim AS production

COPY --from=builder dist dist
RUN pip install --no-cache-dir dist/* && rm -rf dist

ENTRYPOINT ["pyre"]
