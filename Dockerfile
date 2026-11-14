FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY burn ./burn
COPY web ./web
# Processed hotspot data (built locally by burn.fetch_country, burn.fetch_api and burn.ingest).
COPY data/processed ./data/processed
EXPOSE 8080
CMD ["uv", "run", "--no-sync", "uvicorn", "burn.app:app", "--host", "0.0.0.0", "--port", "8080"]
