FROM python:3.12-slim AS builder

RUN apt update && apt install -y curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY . .
RUN uv build --wheel

FROM python:3.12-slim AS production

COPY --from=builder dist dist
RUN pip install --no-cache-dir dist/* && rm -rf dist

ENTRYPOINT ["pyre"]
