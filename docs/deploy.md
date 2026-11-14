# Deploy (BURN-021)

The app is one container: FastAPI serves the API and the static front end, and the processed Parquet data are copied into the image. There are no secrets in the image; `FIRMS_MAP_KEY` is used only on the build machine to fetch 2026 data.

## From a clean checkout

```bash
uv sync
cp .env.example .env                    # add FIRMS_MAP_KEY
uv run python -m burn.fetch_country     # history 2000 to 2025, about 3 GB into data/raw
uv run python -m burn.fetch_api         # 2026 from the FIRMS Area API
uv run python -m burn.ingest            # writes data/processed (about 0.5 GB)
uv run pytest
```

First time only:

```bash
fly auth login
fly launch --no-deploy --copy-config --name <app-name>
```

Every deploy:

```bash
fly deploy
```

Then open `https://<app-name>.fly.dev/` in a private browser window and check that the calendar loads without any login.

## Status

Not deployed yet. Saturday, November 14: the `fly` session on this machine has expired and publishing needs the owner's approval (see `docs/progress-log.md`).
